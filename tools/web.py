"""Make the installable web app: a self-contained site in web/ that GitHub Pages serves and Chrome can install (phone, Retroid).
It plays offline: a service worker keeps every file in a cache named after the build, checks for a newer build in the background and
the game switches to it on the next title screen. Installed, the page drops the on-screen controller and fills the display (.pwa).
The game itself is index.html unchanged, wrapped in a full document (the artifact host normally adds the doctype and head).
usage (from the repo root, after tools/release.py so the build number is current): python3 -I tools/web.py"""
import json, pathlib, re, shutil
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "web"
build = int((ROOT / "tools/build.txt").read_text().strip())
if OUT.exists(): shutil.rmtree(OUT)
(OUT / "art/pixel").mkdir(parents=True); (OUT / "art/title").mkdir(parents=True); (OUT / "fonts").mkdir(); (OUT / "icons").mkdir()

# the game's files, as they are
for f in ["words.js", "studio.js", "art/pixel/atlas.png", "art/pixel/atlas.json", "art/title/glass-lit.png", "art/title/glass-dim.png", "art/title/glass.json"]:
    shutil.copy(ROOT / f, OUT / f)
for f in sorted((ROOT / "tools/fonts").glob("*.woff2")): shutil.copy(f, OUT / "fonts" / f.name)
faces = "".join(f'@font-face{{font-family:"{f.stem.replace("-", " ")}";src:url(fonts/{f.name}) format("woff2");font-display:block}}' for f in sorted((OUT / "fonts").glob("*.woff2")))

# the page: the web fonts come from our own folder instead of the internet
page = (ROOT / "index.html").read_text()
page = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", page)
page = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>', "<style>" + faces + "</style>", page)
assert "fonts.googleapis" not in page and "fonts.gstatic" not in page
page = page.replace("<script>", f"<script>window.LEX_BUILD = {build};</script><script>", 1)
head = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<title>Lexicon Signal</title><meta name="description" content="A late-night radio word game from Idle Looping Studios.">'
        '<link rel="manifest" href="manifest.webmanifest"><meta name="theme-color" content="#0b0806">'
        '<link rel="icon" href="icons/icon-192.png"><link rel="apple-touch-icon" href="icons/icon-192.png">'
        '<meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-capable" content="yes">'
        '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"></head><body>')
(OUT / "index.html").write_text(head + page + '<script src="pwa.js"></script></body></html>')

# icons from our own art: the radio at its true pixel size on the night-room dark, LS lit in the glass as dial dots
atlas = Image.open(ROOT / "art/pixel/atlas.png").convert("RGBA"); aj = json.loads((ROOT / "art/pixel/atlas.json").read_text())
x, y, w, h = aj["rects"]["radio"]; radio = atlas.crop((x, y, x + w, y + h)); pt = aj["points"]["radio"]
g0, g1 = pt["glass0"], pt["glass1"]
L5 = ["10000", "10000", "10000", "10000", "10000", "10000", "11111"]; S5 = ["01111", "10000", "10000", "01110", "00001", "00001", "11110"]
d = ImageDraw.Draw(radio); step = 11; gw, gh = g1[0] - g0[0], g1[1] - g0[1]; tw = (5 * 2 + 2) * step; ox, oy = g0[0] + (gw - tw) // 2 + 3, g0[1] + (gh - 7 * step) // 2 + 3
for li, rows in enumerate([L5, S5]):
    for r, row in enumerate(rows):
        for c, on in enumerate(row):
            cx, cy = ox + (li * 7 + c) * step, oy + r * step
            if on == "1": d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(255, 196, 92, 255)); d.ellipse((cx - 2, cy - 3, cx + 1, cy), fill=(255, 240, 200, 255))
            else: d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=(70, 40, 18, 255))
def icon(size, fit, path):
    im = Image.new("RGBA", (size, size), (11, 8, 6, 255)); glow = Image.new("RGBA", (size, size), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    for k in range(40, 0, -1): a = int(3 * (40 - k) / 40 * 2); r = size * .5 * k / 40; gd.ellipse((size / 2 - r, size / 2 - r, size / 2 + r, size / 2 + r), fill=(90, 40, 14, a))
    im.alpha_composite(glow)
    rw = round(size * fit); s = rw / radio.width
    rr = radio if abs(s - 1) < 1e-6 else radio.resize((rw, round(radio.height * s)), Image.LANCZOS if s < 1 else Image.NEAREST)
    im.alpha_composite(rr, ((size - rr.width) // 2, (size - rr.height) // 2)); im.convert("RGB").save(OUT / "icons" / path)
icon(512, 482 / 512, "icon-512.png"); icon(192, .94, "icon-192.png"); icon(512, .74, "icon-maskable-512.png")

# the manifest: full screen, landscape, dark, installed under the Pages path (start_url and scope are relative to this file)
(OUT / "manifest.webmanifest").write_text(json.dumps({
    "name": "Lexicon Signal", "short_name": "Lexicon Signal", "description": "A late-night radio word game from Idle Looping Studios.",
    "id": "./", "start_url": "./", "scope": "./", "display": "fullscreen", "display_override": ["fullscreen", "standalone"],
    "orientation": "landscape", "background_color": "#0b0806", "theme_color": "#0b0806", "categories": ["games"],
    "icons": [{"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
              {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
              {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, indent=1) + "\n")
(OUT / "version.json").write_text(json.dumps({"build": build}) + "\n")

# pwa.js: marks the installed app and runs the service worker (copied from tools/web/)
shutil.copy(ROOT / "tools/web/pwa.js", OUT / "pwa.js")
files = sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file() and p.name != "version.json")
sw = (ROOT / "tools/web/sw.js").read_text().replace("__BUILD__", str(build)).replace("__FILES__", json.dumps(["./"] + files))
(OUT / "sw.js").write_text(sw)
(OUT / ".nojekyll").write_text("")
print("web app build", build, "->", len(files) + 1, "files")
