// ================================================================
// NHS Personalised Care - Service Worker
// ================================================================

const CACHE_NAME = 'nhs-care-v3';
const STATIC_CACHE = 'nhs-care-static-v3';
const DYNAMIC_CACHE = 'nhs-care-dynamic-v3';

// Assets to cache on install
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
// INSTALL EVENT
// ================================================================
self.addEventListener('install', function(event) {
    console.log('Service Worker: Installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(function(cache) {
                console.log('Service Worker: Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(function() {
                console.log('Service Worker: Install complete');
                return self.skipWaiting();
            })
    );
});

// ================================================================
// ACTIVATE EVENT
// ================================================================
self.addEventListener('activate', function(event) {
    console.log('Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys()
            .then(function(keys) {
                return Promise.all(
                    keys.filter(function(key) {
                        return key !== STATIC_CACHE && key !== DYNAMIC_CACHE;
                    })
                    .map(function(key) {
                        console.log('Service Worker: Removing old cache', key);
                        return caches.delete(key);
                    })
                );
            })
            .then(function() {
                console.log('Service Worker: Activated');
                return self.clients.claim();
            })
    );
});

// ================================================================
// FETCH EVENT - Network First with Cache Fallback
// ================================================================
self.addEventListener('fetch', function(event) {
    const request = event.request;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        event.respondWith(fetch(request));
        return;
    }

    // Skip API requests (they need fresh data)
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(request)
                .then(function(response) {
                    // Cache successful API responses for offline fallback
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
                    // If offline, try cache
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

    // Handle static assets
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

    // Default: Network first with cache fallback
    event.respondWith(
        fetch(request)
            .then(function(response) {
                // Cache successful responses
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
                // Fallback to cache
                return caches.match(request)
                    .then(function(cachedResponse) {
                        if (cachedResponse) {
                            return cachedResponse;
                        }
                        // Return offline page for HTML requests
                        if (request.headers.get('Accept').includes('text/html')) {
                            return caches.match('/');
                        }
                        return new Response('Offline', { status: 503 });
                    });
            })
    );
});

// ================================================================
// PUSH NOTIFICATION EVENT
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

    const options = {
        body: data.body,
        icon: data.icon || '/icons/icon-192.png',
        badge: data.badge || '/icons/icon-72.png',
        vibrate: [200, 100, 200],
        data: {
            url: data.url || '/',
            date: Date.now()
        },
        actions: [
            { action: 'view', title: 'View Now' },
            { action: 'dismiss', title: 'Dismiss' }
        ],
        tag: 'notification-' + Date.now(),
        requireInteraction: true,
        silent: false
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// ================================================================
// NOTIFICATION CLICK EVENT
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
                // Check if there's already a window/tab open with the target URL
                for (let client of windowClients) {
                    if (client.url === url && 'focus' in client) {
                        return client.focus();
                    }
                }
                // If not, open a new window/tab
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
    );
});

// ================================================================
// MESSAGE HANDLING (for updates)
// ================================================================
self.addEventListener('message', function(event) {
    const data = event.data;

    if (data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

// ================================================================
// LOGGING
// ================================================================
console.log('Service Worker: NHS Personalised Care v3 loaded');