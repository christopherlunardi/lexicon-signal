// Lexicon Signal's service worker (made by tools/web.py): keeps every file of one build in its own cache so the game plays offline.
// A newer build installs in the background and waits; the game tells it to take over at the next title screen (message "skip"),
// then the old build's cache is deleted.
const BUILD = 34, CACHE = "lexsig-" + BUILD, FILES = ["./", "art/pixel/atlas.json", "art/pixel/atlas.png", "art/title/glass-dim.png", "art/title/glass-lit.png", "art/title/glass.json", "fonts/Alfa-Slab-One.woff2", "fonts/Special-Elite.woff2", "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png", "index.html", "manifest.webmanifest", "pwa.js", "studio.js", "words.js"];
self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES.map((f) => new Request(f, { cache: "reload" })))));
});
self.addEventListener("message", (e) => { if (e.data === "skip") self.skipWaiting(); else if (e.data === "build" && e.source) e.source.postMessage({ build: BUILD }); });
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k.startsWith("lexsig-") && k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  const req = e.request; if (req.method !== "GET") return;
  const url = new URL(req.url); if (url.origin !== self.location.origin) return;
  if (url.pathname.endsWith("/version.json")) return;   // always asked of the network (the page checks it for a new build)
  e.respondWith(caches.open(CACHE).then((c) => c.match(req, { ignoreSearch: true })
    .then((r) => r || (req.mode === "navigate" ? c.match("./") : undefined))
    .then((r) => r || fetch(req))));
});
