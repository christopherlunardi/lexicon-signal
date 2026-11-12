"""Renders a still of the room at native 480x270 the way the game will: tiled wall, sprites, baked dithered light, palette snap.
Usage: python3 -I art/pixel/preview.py OUT.png [scale]"""
import json, sys
import numpy as np
from PIL import Image
sys.path.insert(0, "art/pixel")
import pix
W, H = 640, 360
meta = json.load(open("art/pixel/sprites.json")); pal = np.array(meta["palette"], float)
# the lit room never uses the glow accents (they are for things that give light), so dithering can't speckle them in
pal = np.array([c for c in pal if tuple(int(v) for v in c) not in set(pix.ACCENTS)], float)
PLACE = {"window": (22, 18), "radio": (172, 14)}          # native top-left of each sprite in the 16:9 layout
t = np.asarray(Image.open("art/pixel/wall_tile.png").convert("RGB")).astype(float)
img = np.tile(t, (H // t.shape[0] + 1, W // t.shape[1] + 1, 1))[:H, :W].copy()
emis = np.zeros((H, W))               # 1 = gives its own light (window glass), skips room lighting
# the sideboard: left end, repeated bay, right end, from x=150 to the right edge of the screen
sbx, sby = 150, 178
parts = ["sb_left"] + ["sb_mid"] * 7 + ["sb_right"]
for nm in parts:
    s = np.asarray(Image.open(f"art/pixel/{nm}.png").convert("RGBA")).astype(float); h, w = s.shape[:2]
    ww_ = min(w, W - sbx)
    if ww_ <= 0: break
    a = s[:, :ww_, 3:] / 255; img[sby:sby + h, sbx:sbx + ww_] = img[sby:sby + h, sbx:sbx + ww_] * (1 - a) + s[:, :ww_, :3] * a
    sbx += w
for name, (px, py) in PLACE.items():
    s = np.asarray(Image.open(f"art/pixel/{name}.png").convert("RGBA")).astype(float)
    h, w = s.shape[:2]; a = s[..., 3:] / 255
    img[py:py + h, px:px + w] = img[py:py + h, px:px + w] * (1 - a) + s[..., :3] * a
    if name == "window":   # glass = blue-ish or bright light pixels inside the frame
        rgb = s[..., :3]; glass = ((rgb[..., 2] > rgb[..., 0] + 10) | (rgb.max(-1) > 200)) & (a[..., 0] > 0)
        glass[:8] = glass[-14:] = False
        emis[py:py + h, px:px + w] = np.maximum(emis[py:py + h, px:px + w], glass)
yy, xx = np.mgrid[0:H, 0:W].astype(float)
lamp = np.clip(1 - np.hypot((xx - 470) / 330, (yy - 200) / 260), 0, 1) ** 1.6
wx, wy = PLACE["window"]; ww, wh = 128, 143
moon = np.clip(1 - np.hypot((xx - (wx + ww / 2)) / 150, (yy - (wy + wh / 2)) / 130), 0, 1) ** 2
light = .42 + lamp[..., None] * np.array([1.05, .78, .5]) + moon[..., None] * np.array([.22, .3, .5])
light *= (1 - .35 * np.clip(np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)) - .6, 0, 1))[..., None]
glass_tint = np.array([.72, .74, .84])   # the view is dimmed and cooled a touch so it sits in the room
lit = img * (light * (1 - emis[..., None]) + glass_tint * emis[..., None])
out = pix.snap(np.clip(lit, 0, 255), pal, dither=.45)
sc = int(sys.argv[2]) if len(sys.argv) > 2 else 3
Image.fromarray(out).resize((W * sc, H * sc), Image.NEAREST).save(sys.argv[1])
