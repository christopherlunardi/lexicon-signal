// Lexicon Signal as an installed web app (made by tools/web.py). Two jobs:
// 1. Installed (full screen or standalone, or added to an iPhone's home screen): add body.pwa, which hides the on-screen controller
//    and lets the screen fill the display. Opened as a normal web page, nothing changes.
// 2. Run the service worker: everything plays from the cache offline; with a network it checks for a newer build in the background,
//    and when one is ready the game switches to it on the next title screen (window.LEX_RELOAD, used by the game's ssUpdateReady).
(function () {
  const mq = ["(display-mode: fullscreen)", "(display-mode: standalone)"].map((q) => matchMedia(q));
  function mark() {
    const on = mq.some((m) => m.matches) || navigator.standalone === true;
    if (on !== document.body.classList.contains("pwa")) { document.body.classList.toggle("pwa", on); dispatchEvent(new Event("resize")); }
  }
  mark(); mq.forEach((m) => m.addEventListener && m.addEventListener("change", mark));

  if (!("serviceWorker" in navigator)) return;
  let swapping = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => { if (swapping) location.reload(); });
  navigator.serviceWorker.register("sw.js").then((reg) => {
    const ready = (w) => {
      window.LEX_RELOAD = () => { swapping = true; w.postMessage("skip"); };
      fetch("version.json", { cache: "no-store" }).then((r) => r.json()).then((v) => v.build).catch(() => "")
        .then((b) => { if (window.ssUpdateReady) window.ssUpdateReady(b || "NEW"); });
    };
    const watch = (w) => { if (w) w.addEventListener("statechange", () => { if (w.state === "installed" && navigator.serviceWorker.controller) ready(w); }); };
    if (reg.waiting && navigator.serviceWorker.controller) ready(reg.waiting);
    reg.addEventListener("updatefound", () => watch(reg.installing));
    if (navigator.onLine !== false) reg.update().catch(() => {});
  }).catch(() => {});
})();
