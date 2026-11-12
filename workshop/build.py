"""Makes the Workshop's playable copy of the game: play.html (the game page wrapped as a full document) plus the files it loads.
Options link to it with a hash (e.g. play.html#keys-2). Run from the repo root: python3 -I workshop/build.py
play.html, words.js and art/ in workshop/ are generated copies (not kept in git)."""
import shutil, os
W = "workshop/"
page = open("index.html").read()
open(W + "play.html", "w").write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>' + page + "</body></html>")
os.makedirs(W + "art/pixel", exist_ok=True)
shutil.copy("words.js", W + "words.js"); shutil.copy("studio.js", W + "studio.js"); shutil.copy("art/pixel/atlas.png", W + "art/pixel/atlas.png"); shutil.copy("art/pixel/atlas.json", W + "art/pixel/atlas.json")
print("play copy ready")
