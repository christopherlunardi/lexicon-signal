"""Make a new build for the Retroid app: the whole game as ONE html file (words, studio intro, art and fonts inside it, so the app can
play it offline from a file) in dist/lexicon-signal.html, with dist/version.json (build number, size, sha256). The app on the
handheld compares its build with dist/version.json on GitHub (main) and downloads the new page when it's newer, replacing the old one,
so a release reaches the Retroids as soon as it's pushed. The phone link (the artifact) is published separately, as before.
usage: python3 -I tools/release.py"""
import base64, datetime, hashlib, json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
bt = ROOT / "tools/build.txt"; build = (int(bt.read_text().strip()) if bt.exists() else 0) + 1; bt.write_text(str(build) + "\n")
page = (ROOT / "index.html").read_text()
b64 = lambda p: base64.b64encode((ROOT / p).read_bytes()).decode()
assets = {"atlasJson": json.loads((ROOT / "art/pixel/atlas.json").read_text()), "atlasPng": "data:image/png;base64," + b64("art/pixel/atlas.png"),
          "glassJson": json.loads((ROOT / "art/title/glass.json").read_text()), "glassLit": "data:image/png;base64," + b64("art/title/glass-lit.png"),
          "glassDim": "data:image/png;base64," + b64("art/title/glass-dim.png")}
inline = lambda f: "<script>" + (ROOT / f).read_text().replace("</script", "<\\/script") + "</script>"
page = page.replace('<script src="words.js"></script>', inline("words.js")).replace('<script src="studio.js"></script>', inline("studio.js"))
assert "words.js" not in re.findall(r'<script src="[^"]+"', page) and 'src="studio.js"' not in page
page = page.replace("<script>", "<script>window.LEX_ASSETS = " + json.dumps(assets) + "; window.LEX_BUILD = " + str(build) + ";</script><script>", 1)
# the web fonts, inside the page too (offline): the faces the game draws with
fonts = ROOT / "tools/fonts"; faces = "".join(f'@font-face{{font-family:"{f.stem.replace("-", " ")}";src:url(data:font/woff2;base64,{base64.b64encode(f.read_bytes()).decode()}) format("woff2")}}' for f in sorted(fonts.glob("*.woff2")))
page = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", page); page = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>', "<style>" + faces + "</style>", page)
html = ('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>' + page + "</body></html>").encode()
(ROOT / "dist").mkdir(exist_ok=True); (ROOT / "dist/lexicon-signal.html").write_bytes(html)
(ROOT / "dist/version.json").write_text(json.dumps({"build": build, "bytes": len(html), "sha256": hashlib.sha256(html).hexdigest(),
  "made": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")}, indent=1) + "\n")
print("released build", build, len(html), "bytes")
