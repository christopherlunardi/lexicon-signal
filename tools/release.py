"""Make a new build: bumps the build number in tools/build.txt (the GitHub site's web app and the game show it) and checks
index.html for code after a // comment on the same line. Then run tools/web.py and publish the phone link.
(The one-file dist/ page for the retired Android app is no longer made: Chris plays on the GitHub site, 2026-11-22.)
usage: python3 -I tools/release.py"""
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
page = (ROOT / "index.html").read_text()
# a // comment in the middle of a line silently cuts off the code after it (it hid the part picker's plates once): refuse to release
bad = [n for n, l in enumerate(page.split("\n"), 1) if re.search(r"[;}]\s+// \([^)]*\)\s*[^\s/]", l)]
if bad: sys.exit("code after a // comment on line(s) " + ", ".join(map(str, bad)) + " of index.html: move the comment to the end")
bt = ROOT / "tools/build.txt"; build = (int(bt.read_text().strip()) if bt.exists() else 0) + 1; bt.write_text(str(build) + "\n")
print("released build", build)
