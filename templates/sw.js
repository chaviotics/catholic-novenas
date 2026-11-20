/* Catholic Novenas service worker: keeps the whole library on this device so it opens without signal.
   Pages: network first (corrections arrive right away), the saved copy when offline or after {{TIMEOUT}} ms.
   Everything else (images, fonts, icons): saved once and reused. Built by tools/build.py; do not edit site/sw.js. */
var VERSION = "{{VERSION}}";
var CACHE = "novenas-" + VERSION;
var FILES = {{FILES}};
var TIMEOUT = {{TIMEOUT}};

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
      var u = new URL(req.url), key = u.origin + u.pathname;
      var net = fetch(req).then(clean).then(function(r){ if (r && r.ok) c.put(key, r.clone()); return r; });
      var saved = c.match(key).then(function(m){
        if (m) return m;
        var dir = /\/$/.test(u.pathname) ? u.pathname : (/\.html$/.test(u.pathname) ? null : u.pathname + "/");
        return dir ? c.match(u.origin + dir + "index.html") : null;
      }).then(function(m){ return m || c.match(url("index.html")); });
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
