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
    # the sideboard is cut into a left end, one repeating drawer bay and a right end, so it stretches to any width
    "sb_left": {"src": "sideboard.png", "scale": .2, "crop": (12, 360, 72, 589)},
    "sb_mid": {"src": "sideboard.png", "scale": .2, "crop": (72, 360, 327, 589)},
    "sb_right": {"src": "sideboard.png", "scale": .2, "crop": (1585, 360, 1647, 589)},
    # interface kit (one scale for every piece): the bar stretches (left end, plain middle, right end) with the clasp centred on top
    "bar_left": {"src": "uikit.png", "scale": .217, "crop": (14, 112, 138, 416)},
    "bar_mid": {"src": "uikit.png", "scale": .217, "crop": (300, 112, 558, 416)},
    "bar_right": {"src": "uikit.png", "scale": .217, "crop": (1524, 112, 1648, 416)},
    "bar_clasp": {"src": "uikit.png", "scale": .217, "crop": (762, 112, 900, 170)},
    "logbox": {"src": "uikit.png", "scale": .217, "crop": (24, 538, 642, 800)},
    "plate": {"src": "uikit.png", "scale": .217, "crop": (674, 554, 1004, 646)},
    "battery": {"src": "uikit.png", "scale": .217, "crop": (1040, 602, 1290, 720), "points": {"seg0": (1066, 632), "seg1": (1266, 690)}},
    "slot": {"src": "uikit.png", "scale": .217, "crop": (1320, 554, 1508, 760)},
    "button": {"src": "uikit.png", "scale": .217, "crop": (1540, 610, 1634, 704)},
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
        if "crop" in s: x0, y0, x1, y1 = s["crop"]
        W = s["w"] if "w" in s else round((x1 - x0) * s["scale"])
        H = round(W * (y1 - y0) / (x1 - x0)) if "w" in s else round((y1 - y0) * s["scale"])
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

# ---------------- icons, fonts and the atlas the game loads ----------------
from PIL import ImageDraw, ImageFont
ICON_NAMES = ["amp", "battery", "vowel", "filter", "coil", "echo", "owl", "knob", "treble", "short", "carrier", "fuse"]
FONTS = {"small": ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 8),
         "big": ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)}
CHARS = "".join(chr(c) for c in range(32, 96)) + "u"

def icons(pal):
    a, alpha, _ = keyed(SRC + "icons.png")
    Hh, Ww = alpha.shape; out = {}
    for k, name in enumerate(ICON_NAMES):
        cx0, cy0 = (k % 4) * Ww // 4, (k // 4) * Hh // 3
        al = alpha[cy0:cy0 + Hh // 3, cx0:cx0 + Ww // 4]; ys, xs = np.where(al)
        x0, x1, y0, y1 = cx0 + xs.min(), cx0 + xs.max() + 1, cy0 + ys.min(), cy0 + ys.max() + 1
        s = 27 / max(x1 - x0, y1 - y0); W, H = max(1, round((x1 - x0) * s)), max(1, round((y1 - y0) * s))
        crop = a[y0:y1, x0:x1]; m = alpha[y0:y1, x0:x1]
        rgb = np.asarray(Image.fromarray((crop * m[..., None]).astype("uint8")).resize((W, H), Image.BOX)).astype(float)
        cov = np.asarray(Image.fromarray((m * 255).astype("uint8")).resize((W, H), Image.BOX)).astype(float) / 255
        col = pix.snap(np.clip(rgb / np.maximum(cov[..., None], 1e-3), 0, 255), pal)
        out["icon_" + name] = Image.fromarray(np.dstack([col, (cov > .5).astype(np.uint8) * 255]), "RGBA")
    return out

def glyphs():
    out, metrics = {}, {}
    for fname, (path, size) in FONTS.items():
        f = ImageFont.truetype(path, size); asc, desc = f.getmetrics(); h = asc + desc
        metrics[fname] = {"h": h, "adv": {}}
        for ch in CHARS:
            key = "Qu" if ch == "u" else ch
            if ch == "u" and fname != "big": continue
            txt = "Qu" if ch == "u" else ch
            w = max(1, int(round(f.getlength(txt))))
            im = Image.new("L", (w + 2, h + 2), 0); d = ImageDraw.Draw(im); d.fontmode = "1"; d.text((1, 1), txt, font=f, fill=255)
            rgba = Image.new("RGBA", im.size, (255, 255, 255, 0)); rgba.putalpha(im.point(lambda v: 255 if v > 127 else 0))
            out[f"g_{fname}_{ord(ch) if key != 'Qu' else 'Qu'}"] = rgba; metrics[fname]["adv"][key] = w
    return out, metrics

def atlas(meta, pal):
    imgs = {n: Image.open(OUT + n + ".png").convert("RGBA") for n in meta["sprites"]}
    # the window glass mask: which window pixels give their own light (the night view), so room light skips them
    win = np.asarray(imgs["window"]).astype(int); rgb = win[..., :3]
    seen = ((rgb[..., 2] > rgb[..., 0] + 10) | (rgb.max(-1) > 200)) & (win[..., 3] > 0); seen[:8] = seen[-14:] = False
    ys, xs = np.where(seen); inside = np.zeros_like(seen); inside[ys.min():ys.max() + 1, xs.min():xs.max() + 1] = True
    wood = (rgb[..., 0] > rgb[..., 2] + 25) & (rgb[..., 0] > 60) & ~(rgb.max(-1) > 200)   # frame bars, not lit windows
    glass = inside & ~wood & (win[..., 3] > 0)
    imgs["window_glass"] = Image.fromarray(np.dstack([np.full(glass.shape + (3,), 255, np.uint8), glass.astype(np.uint8) * 255]), "RGBA")
    imgs.update(icons(pal))
    g, metrics = glyphs(); imgs.update(g)
    # shelf packing
    order = sorted(imgs, key=lambda n: -imgs[n].height); AW = 1024; x = y = sh = 0; rects = {}
    for n in order:
        w, h = imgs[n].size
        if x + w > AW: x = 0; y += sh + 1; sh = 0
        rects[n] = [x, y, w, h]; x += w + 1; sh = max(sh, h)
    AH = y + sh + 1; sheet = Image.new("RGBA", (AW, AH), (0, 0, 0, 0))
    for n, (x, y, w, h) in rects.items(): sheet.alpha_composite(imgs[n], (x, y))
    sheet.save(OUT + "atlas.png", optimize=True)
    pts = {n: s.get("points", {}) for n, s in meta["sprites"].items()}
    json.dump({"palette": meta["palette"], "accents": [list(c) for c in pix.ACCENTS], "rects": rects, "points": pts, "fonts": metrics},
              open(OUT + "atlas.json", "w"))
    print("atlas", AW, AH, len(rects), "pieces")

atlas(json.load(open(OUT + "sprites.json")), np.array(json.load(open(OUT + "sprites.json"))["palette"], float))
