
const CACHE_NAME = 'nhs-care-v2';
const ASSETS = ['/', '/manifest.json', '/api/health'];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) { return cache.addAll(ASSETS); })
            .then(function() { return self.skipWaiting(); })
    );
});

self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys()
            .then(function(keys) {
                return Promise.all(keys.filter(function(k) { return k !== CACHE_NAME; }).map(function(k) { return caches.delete(k); }));
            })
            .then(function() { return self.clients.claim(); })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) { return response || fetch(event.request); })
            .catch(function() { return new Response('Offline', { status: 503 }); })
    );
});

self.addEventListener('push', function(event) {
    var data = event.data ? event.data.json() : { title: 'NHS Care', body: 'Update available' };
    event.waitUntil(
        self.registration.showNotification(data.title || 'NHS Care', {
            body: data.body || 'You have a new update',
            icon: '/icons/icon-192.png',
            badge: '/icons/icon-72.png'
        })
    );
});
