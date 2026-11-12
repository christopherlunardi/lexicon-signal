"""Builds every pixel-art sprite from the ChatGPT sources in art/pixel/src/.
1. Master palette (64 colours) from the look target and all sources, so every layer shares the same colours.
2. Each sprite: key out magenta, crop, shrink to its native size (the game's 480x270 world), hard 1-bit alpha, snap to the palette.
3. sprites.json: sizes plus marked points (like the tower beacon) in native pixels.
Run from the repo root: python3 -I art/pixel/build.py"""
import json, sys
import numpy as np
from PIL import Image
sys.path.insert(0, "art/pixel")
import pix

SRC = "art/pixel/src/"
OUT = "art/pixel/"
# name: source file, native width (height follows), points of interest in source pixels (found by eye / measured)
SPRITES = {
    "window": {"src": "window.png", "w": 128, "points": {"beacon": (648, 574)}},
    "radio": {"src": "radio.png", "w": 292, "points": {
        "glass0": (552, 214), "glass1": (1102, 688), "dial0": (462, 84), "dial1": (1148, 150), "meter": (1312, 146), "meterR": (1392, 146),
        "lamp0": (583, 783), "lamp1": (678, 783), "lamp2": (773, 783), "lamp3": (868, 783), "lamp4": (963, 783), "lamp5": (1062, 783),
        "knobL": (358, 745), "knobR": (1300, 745)}},
}
TILES = {"wall_tile": {"src": "wallpaper.png", "period": (156, 138), "native": (24, 21), "area": (150, 160)}}

def keyed(path):
    a = np.asarray(Image.open(path).convert("RGB")).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    alpha = (np.minimum(r, b) - g) < 110          # not magenta
    ys, xs = np.where(alpha)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    return a, alpha, box

def main():
    sources = [("art/concept/look-target.png", (480, 274)), (SRC + "wallpaper.png", (240, 137))]
    for s in SPRITES.values():
        a, alpha, (x0, y0, x1, y1) = keyed(SRC + s["src"])
        sources.append((SRC + s["src"], (max(8, (x1 - x0) // 8), max(8, (y1 - y0) // 8))))
    pal = pix.build_palette(sources, 64)
    meta = {"palette": pal.tolist(), "sprites": {}}
    for name, t in TILES.items():
        a = np.asarray(Image.open(SRC + t["src"]).convert("RGB")).astype(float)
        PX, PY = t["period"]; X0, Y0 = t["area"]
        reps = [a[y:y + PY, x:x + PX] for y in range(Y0, a.shape[0] - PY - 20, PY) for x in range(X0, a.shape[1] - PX - 20, PX)]
        tile = np.median(np.stack(reps), 0)
        small = np.asarray(Image.fromarray(tile.astype("uint8")).resize(t["native"], Image.BOX)).astype(float)
        Image.fromarray(pix.snap(small, pal)).save(OUT + name + ".png")
        meta["sprites"][name] = {"w": t["native"][0], "h": t["native"][1], "tile": True}
    for name, s in SPRITES.items():
        a, alpha, (x0, y0, x1, y1) = keyed(SRC + s["src"])
        W = s["w"]; H = round(W * (y1 - y0) / (x1 - x0))
        crop = a[y0:y1, x0:x1]; al = alpha[y0:y1, x0:x1]
        # shrink colour using only opaque source pixels, so magenta never bleeds into edges
        rgb = Image.fromarray((crop * al[..., None]).astype("uint8")).resize((W, H), Image.BOX)
        cov = Image.fromarray((al * 255).astype("uint8")).resize((W, H), Image.BOX)
        rgbn = np.asarray(rgb).astype(float); covn = np.asarray(cov).astype(float) / 255
        col = rgbn / np.maximum(covn[..., None], 1e-3)
        snapped = pix.snap(np.clip(col, 0, 255), pal)
        a8 = (covn > .5).astype(np.uint8) * 255
        Image.fromarray(np.dstack([snapped, a8]), "RGBA").save(OUT + name + ".png")
        sx, sy = W / (x1 - x0), H / (y1 - y0)
        pts = {k: [round((px - x0) * sx), round((py - y0) * sy)] for k, (px, py) in s.get("points", {}).items()}
        meta["sprites"][name] = {"w": W, "h": H, "points": pts}
    json.dump(meta, open(OUT + "sprites.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in meta["sprites"].items()}))

main()
