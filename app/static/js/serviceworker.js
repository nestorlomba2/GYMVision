var staticCacheName = 'djangopwa-v1';
var appRequest = new Request('/', { credentials: 'include' });
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(staticCacheName).then(function(cache) {
      return cache.addAll([
        '/images/logo_recortado.jpg',
      ]);
    })
  );
});

// Clear cache on activate
// self.addEventListener('activate', event => {
//   event.waitUntil(
//       caches.keys().then(cacheNames => {
//           return Promise.all(
//               cacheNames
//                   .filter(cacheName => (cacheName.startsWith("djangopwa-")))
//                   .filter(cacheName => (cacheName !== staticCacheName))
//                 /*  */  .map(cacheName => caches.delete(cacheName))
//           );
//       })
//   );
// });

self.addEventListener('activate', event => {
  //if url is /logout/ then clear cache
  var requestUrl = new URL(event.request.url);
  if (requestUrl.pathname === 'http://http://127.0.0.1:8000/login/') {
    console.log("clearing cache");
    event.waitUntil(
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(cacheName => (cacheName.startsWith("djangopwa-")))
            // .filter(cacheName => (cacheName !== staticCacheName))
            .map(cacheName => caches.delete(cacheName))
        );
      })
    );



  }

})
// Serve from Cache*
// self.addEventListener('fetch', function(event) {
//   var requestUrl = new URL(event.request.url);
//     if (requestUrl.origin === location.origin) {
//       if ((requestUrl.pathname === '/' )) {
//         console.log('getting cache');
//         event.respondWith(caches.match('/'));
//         return;
//       }
//     }
//     event.respondWith(
//       caches.match(event.request).then(function(response) {
//         return response || fetch(event.request);
//       })
//     );
// });