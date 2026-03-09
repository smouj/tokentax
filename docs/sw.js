const CACHE_NAME = 'tokentax-v5.2';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './model_prices_and_context_window.json'
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
  if (event.request.method !== 'GET') return;

  const url = event.request.url;
  const isSameOrigin = new URL(url).origin === self.location.origin;
  const isAllowedCrossOrigin =
    url.includes('litellm') ||
    url.includes('raw.githubusercontent.com') ||
    url.includes('fonts.googleapis.com') ||
    url.includes('fonts.gstatic.com') ||
    url.includes('cdn.tailwindcss.com') ||
    url.includes('cdnjs.cloudflare.com');

  if (!isSameOrigin && !isAllowedCrossOrigin) return;

  event.respondWith(
    fetch(event.request)
      .then(response => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
