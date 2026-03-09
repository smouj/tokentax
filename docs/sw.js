const CACHE_NAME = 'tokentax-v5.1';
const ASSETS = [
  '/',
  '/index.html',
  '/manifest.json'
];

// Install - cache assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('Caching app assets');
      return cache.addAll(ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate - clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => 
      Promise.all(
        keys.filter(k => k !== CACHE_NAME)
            .map(k => { console.log('Deleting old cache:', k); return caches.delete(k); })
      )
    )
  );
  self.clients.claim();
});

// Fetch - network first, fallback to cache
self.addEventListener('fetch', event => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;
  
  // Skip cross-origin except LiteLLm and fonts
  const url = event.request.url;
  if (!url.includes('litellm') && 
      !url.includes('raw.githubusercontent.com') &&
      !url.includes('fonts.googleapis.com') &&
      !url.includes('fonts.gstatic.com') &&
      !url.includes('cdn.tailwindcss.com') &&
      !url.includes('cdnjs.cloudflare.com')) {
    return;
  }
  
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Clone and cache successful responses
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => {
        // Fallback to cache
        return caches.match(event.request);
      })
  );
});
