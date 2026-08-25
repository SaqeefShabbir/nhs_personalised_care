// ================================================================
// NHS Personalised Care - Service Worker v3
// ================================================================

const CACHE_NAME = 'nhs-care-v3';
const STATIC_CACHE = 'nhs-care-static-v3';
const DYNAMIC_CACHE = 'nhs-care-dynamic-v3';

const STATIC_ASSETS = [
    '/',
    '/manifest.json',
    '/api/health',
    '/icons/icon-72.png',
    '/icons/icon-96.png',
    '/icons/icon-128.png',
    '/icons/icon-144.png',
    '/icons/icon-152.png',
    '/icons/icon-192.png',
    '/icons/icon-384.png',
    '/icons/icon-512.png'
];

// ================================================================
// INSTALL
// ================================================================
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(function(cache) {
                return cache.addAll(STATIC_ASSETS);
            })
            .then(function() {
                return self.skipWaiting();
            })
    );
});

// ================================================================
// ACTIVATE
// ================================================================
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys()
            .then(function(keys) {
                return Promise.all(
                    keys.filter(function(key) {
                        return key !== STATIC_CACHE && key !== DYNAMIC_CACHE;
                    })
                    .map(function(key) {
                        return caches.delete(key);
                    })
                );
            })
            .then(function() {
                return self.clients.claim();
            })
    );
});

// ================================================================
// FETCH
// ================================================================
self.addEventListener('fetch', function(event) {
    const request = event.request;
    const url = new URL(request.url);

    if (request.method !== 'GET') {
        event.respondWith(fetch(request));
        return;
    }

    // API requests - network first with cache fallback
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(request)
                .then(function(response) {
                    if (response && response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(DYNAMIC_CACHE)
                            .then(function(cache) {
                                cache.put(request, responseClone);
                            });
                    }
                    return response;
                })
                .catch(function() {
                    return caches.match(request)
                        .then(function(cachedResponse) {
                            if (cachedResponse) {
                                return cachedResponse;
                            }
                            return new Response(JSON.stringify({
                                success: false,
                                error: 'Offline - Please connect to the internet'
                            }), {
                                status: 503,
                                headers: { 'Content-Type': 'application/json' }
                            });
                        });
                })
        );
        return;
    }

    // Static assets - cache first
    if (url.pathname.match(/\.(css|js|png|jpg|jpeg|svg|ico|json)$/)) {
        event.respondWith(
            caches.match(request)
                .then(function(cachedResponse) {
                    if (cachedResponse) {
                        // Update cache in background
                        fetch(request)
                            .then(function(response) {
                                if (response && response.status === 200) {
                                    caches.open(STATIC_CACHE)
                                        .then(function(cache) {
                                            cache.put(request, response);
                                        });
                                }
                            })
                            .catch(function() {});
                        return cachedResponse;
                    }
                    return fetch(request);
                })
        );
        return;
    }

    // HTML pages - network first with cache fallback
    event.respondWith(
        fetch(request)
            .then(function(response) {
                if (response && response.status === 200) {
                    const responseClone = response.clone();
                    caches.open(DYNAMIC_CACHE)
                        .then(function(cache) {
                            cache.put(request, responseClone);
                        });
                }
                return response;
            })
            .catch(function() {
                return caches.match(request)
                    .then(function(cachedResponse) {
                        if (cachedResponse) {
                            return cachedResponse;
                        }
                        if (request.headers.get('Accept').includes('text/html')) {
                            return caches.match('/');
                        }
                        return new Response('Offline', { status: 503 });
                    });
            })
    );
});

// ================================================================
// PUSH NOTIFICATIONS
// ================================================================
self.addEventListener('push', function(event) {
    let data = {
        title: 'NHS Personalised Care',
        body: 'You have a new health update',
        icon: '/icons/icon-192.png',
        badge: '/icons/icon-72.png',
        url: '/'
    };

    if (event.data) {
        try {
            const parsed = event.data.json();
            data = { ...data, ...parsed };
        } catch (e) {
            data.body = event.data.text();
        }
    }

    event.waitUntil(
        self.registration.showNotification(data.title, {
            body: data.body,
            icon: data.icon,
            badge: data.badge,
            vibrate: [200, 100, 200],
            data: { url: data.url },
            actions: [
                { action: 'view', title: 'View Now' },
                { action: 'dismiss', title: 'Dismiss' }
            ],
            tag: 'notification-' + Date.now(),
            requireInteraction: true
        })
    );
});

// ================================================================
// NOTIFICATION CLICK
// ================================================================
self.addEventListener('notificationclick', function(event) {
    event.notification.close();

    if (event.action === 'dismiss') {
        return;
    }

    const url = event.notification.data?.url || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(function(windowClients) {
                for (let client of windowClients) {
                    if (client.url === url && 'focus' in client) {
                        return client.focus();
                    }
                }
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
    );
});