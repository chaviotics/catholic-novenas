/* Catholic Novenas service worker: keeps the whole library on this device so it opens without signal.
   Pages: network first (corrections arrive right away), the saved copy when offline or after 4000 ms.
   Everything else (images, fonts, icons): saved once and reused. Built by tools/build.py; do not edit site/sw.js. */
var VERSION = "7fc8a72b84f6";
var CACHE = "novenas-" + VERSION;
var FILES = ["apple-touch-icon.png", "favicon.svg", "icon-192.png", "icon-512.png", "index.html", "./", "manifest.webmanifest", "fonts/cormorant-garamond-italic.woff2", "fonts/cormorant-garamond.woff2", "fonts/eb-garamond-italic.woff2", "fonts/eb-garamond.woff2", "fonts/fonts.css", "healing/index.html", "healing/", "healing/img/bernadette.jpg", "healing/img/bernadette_face.jpg", "healing/img/camillus.jpg", "healing/img/camillus_face.jpg", "healing/img/mary_face.jpg", "healing/img/raphael.jpg", "healing/img/raphael_face.jpg", "relief-from-debt/index.html", "relief-from-debt/", "relief-from-debt/img/joseph.jpg", "relief-from-debt/img/joseph_face.jpg", "relief-from-debt/img/jude.jpg", "relief-from-debt/img/jude_face.jpg", "relief-from-debt/img/mary_face.jpg", "relief-from-debt/img/rita.jpg", "relief-from-debt/img/rita_face.jpg"];
var TIMEOUT = 4000;

function url(p){ return new URL(p, self.registration.scope).href; }
/* a redirected response can't answer a page request, so keep only its body */
function clean(r){
  if (!r || !r.redirected) return Promise.resolve(r);
  return r.blob().then(function(b){ return new Response(b, {status: r.status, statusText: r.statusText, headers: r.headers}); });
}
function isPage(req){ return req.mode === "navigate" || (req.headers.get("accept") || "").indexOf("text/html") >= 0; }

self.addEventListener("install", function(e){
  e.waitUntil(caches.open(CACHE).then(function(c){
    return Promise.all(FILES.map(function(p){
      return fetch(url(p), {cache: "no-cache"}).then(function(r){
        if (!r.ok) throw new Error(p + " " + r.status);
        return clean(r).then(function(cr){ return c.put(url(p), cr); });
      });
    }));
  }).then(function(){ return self.skipWaiting(); }));
});

self.addEventListener("activate", function(e){
  e.waitUntil(caches.keys().then(function(keys){
    return Promise.all(keys.filter(function(k){ return k.indexOf("novenas-") === 0 && k !== CACHE; }).map(function(k){ return caches.delete(k); }));
  }).then(function(){ return self.clients.claim(); }));
});

self.addEventListener("fetch", function(e){
  var req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;
  if (isPage(req)){
    e.respondWith(caches.open(CACHE).then(function(c){
      var net = fetch(req).then(clean).then(function(r){ if (r && r.ok) c.put(req.url.split("#")[0], r.clone()); return r; });
      var saved = c.match(req, {ignoreSearch: true}).then(function(m){
        if (m) return m;
        var u = new URL(req.url); if (/\/$/.test(u.pathname)) return c.match(u.origin + u.pathname + "index.html");
        return null;
      });
      return new Promise(function(resolve){
        var done = false;
        function give(r){ if (!done && r){ done = true; resolve(r); } }
        var t = setTimeout(function(){ saved.then(give); }, TIMEOUT);
        net.then(function(r){ clearTimeout(t); give(r); }, function(){ clearTimeout(t); saved.then(function(m){ give(m || Response.error()); }); });
      });
    }));
    return;
  }
  e.respondWith(caches.open(CACHE).then(function(c){
    return c.match(req, {ignoreSearch: true}).then(function(m){
      return m || fetch(req).then(function(r){ if (r && r.ok && r.type === "basic") c.put(req, r.clone()); return r; });
    });
  }));
});
