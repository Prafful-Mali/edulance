var staticCacheName = 'edulance-v1';

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(staticCacheName).then(function(cache) {
            return cache.addAll([
                '/',
                '/dashboard/',
                '/collaborate/',
                '/static/base.css',
                '/static/base.js',
                '/static/dashboard/css/dashboard.css',
                '/static/dashboard/js/dashboard.js',
                '/static/post/collaborate/collaborate.css',
                '/static/post/collaborate/collaborate.js',
            ]);
        })
    );
});

self.addEventListener('fetch', function(event) {
    var requestUrl = new URL(event.request.url);
    
    // Skip cross-origin requests
    if (requestUrl.origin !== location.origin) {
        return;
    }
    
    // Skip API calls for fresh data
    if (requestUrl.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(event.request).catch(function() {
                return new Response(
                    JSON.stringify({ error: 'Network unavailable' }),
                    { 
                        headers: { 'Content-Type': 'application/json' },
                        status: 503
                    }
                );
            })
        );
        return;
    }
    
    // Cache-first strategy
    event.respondWith(
        caches.match(event.request).then(function(response) {
            return response || fetch(event.request);
        })
    );
});

self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(cacheName) {
                    return cacheName.startsWith('edulance-') && cacheName !== staticCacheName;
                }).map(function(cacheName) {
                    return caches.delete(cacheName);
                })
            );
        })
    );
});