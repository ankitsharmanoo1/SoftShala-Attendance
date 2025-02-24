const CACHE_NAME = "pwa-cache-v2";  // Changed cache name to force update
const urlsToCache = [
    "/",
    "/static/styles.css",
    "/static/app.js",
    "/static/downloads.png",
    "/static/smartphone-call.png"
];

// Install Event: Cache Files
self.addEventListener("install", (event) => {
    self.skipWaiting();  // Force service worker to activate immediately
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log("Opened cache");
            return cache.addAll(urlsToCache);
        })
    );
});

// Fetch Event: Serve from network first, fallback to cache
self.addEventListener("fetch", (event) => {
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                return response;
            })
            .catch(() => caches.match(event.request)) 
    );
});

// Activate Event: Remove old caches
self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((cacheName) => cacheName !== CACHE_NAME)
                    .map((cacheName) => caches.delete(cacheName))
            );
        })
    );
});
