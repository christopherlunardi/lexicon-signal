"""Embed the game's fonts in index.html (Chris 2026-11-16: get it ready for packaging; no fonts from the internet).
The font files and their licenses live in tools/fonts/. This writes them as data URIs into the <style id="fonts"> block of
index.html (made if missing, replacing the old Google Fonts links). Run it again whenever a font is added or changed:
    python3 -I tools/fonts.py
Fonts: Alfa Slab One (OFL), Silkscreen (OFL), Special Elite (Apache 2.0), Bungee (OFL, cut to Latin letters)."""
import base64, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
page = (ROOT / "index.html").read_text()
faces = ""
for f in sorted((ROOT / "tools/fonts").glob("*.woff2")):
    b = base64.b64encode(f.read_bytes()).decode()
    faces += '@font-face{font-family:"%s";src:url(data:font/woff2;base64,%s) format("woff2");font-display:block}\n' % (f.stem.replace("-", " "), b)
block = '<style id="fonts">\n/* the game\'s own fonts, embedded (tools/fonts.py writes this block; licenses in tools/fonts/) */\n' + faces + "</style>"
page = re.sub(r'<link rel="preconnect" href="https://fonts\.g[^>]*>\n?', "", page)
if '<style id="fonts">' in page: page = re.sub(r'<style id="fonts">.*?</style>', lambda m: block, page, flags=re.S)
else: page = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>', lambda m: block, page)
assert "fonts.googleapis" not in page and "fonts.gstatic" not in page and '<style id="fonts">' in page
(ROOT / "index.html").write_text(page)
print("embedded", len(list((ROOT / "tools/fonts").glob("*.woff2"))), "fonts,", len(faces) // 1024, "KB")
