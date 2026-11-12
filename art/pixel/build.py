"""Builds every pixel-art sprite for the game from the art in art/pixel/src/.

ChatGPT's "pixel art" is a big image of fake pixels of uneven size. Each source was run once through a pixel-grid fixer, which
recovered its real pixel grid; that result is saved next to it as NAME_fixed.png. Sprites are cut from the fixed images at exactly
their own pixel size: never resized, never forced into a small palette, so every pixel stays clean. (The interface kit came back
with tall pixels, so its rows are evened out to square pixels first.)

Crops and points below are written in the ORIGINAL source's pixels (easy to measure on the big image) and converted to the fixed
image's pixels. Outputs: atlas.png + atlas.json (palette for interface colours, sprite rectangles, marked points).
Run from the repo root: python3 -I art/pixel/build.py"""
import json, sys
import numpy as np
from scipy import ndimage
from PIL import Image
sys.path.insert(0, "art/pixel")
import pix

SRC = "art/pixel/src/"
OUT = "art/pixel/"
SQUARE = {"uikit": 3.197}     # sources whose fixed rows need evening out: real pixel size in source px (both axes)
SPRITES = {
    # the window (2026-11-12, Chris picked design 7 of 9: tall, stained glass across the top). Its source had no recoverable grid, so
    # window7_fixed.png is a k-centroid downscale (art/pixel/kdown.py) to 141x233: same width as before, taller.
    "window": {"src": "window7", "points": {"beacon": (174.5, 210.5)}},
    "radio": {"src": "radio", "points": {
        "glass0": (552, 214), "glass1": (1102, 688), "dial0": (462, 84), "dial1": (1148, 150), "meter": (1312, 146), "meterR": (1392, 146),
        "lamp0": (583, 783), "lamp1": (678, 783), "lamp2": (773, 783), "lamp3": (868, 783), "lamp4": (963, 783), "lamp5": (1062, 783),
        "knobL": (358, 745), "knobR": (1300, 745)}},
    # the sideboard is a left end, one repeating drawer bay and a right end, so it stretches to any width
    "sb_left": {"src": "sideboard", "crop": (12, 360, 72, 589)},
    "sb_mid": {"src": "sideboard", "crop": (72, 360, 327, 589)},
    "sb_right": {"src": "sideboard", "crop": (1585, 360, 1647, 589)},
    # interface kit: the bar stretches (left end, plain middle, right end) with the clasp centred on top
    "bar_left": {"src": "uikit", "crop": (14, 112, 138, 416)},
    "bar_mid": {"src": "uikit", "crop": (300, 112, 558, 416)},
    "bar_right": {"src": "uikit", "crop": (1524, 112, 1648, 416)},
    "bar_clasp": {"src": "uikit", "crop": (762, 112, 900, 170)},
    "logbox": {"src": "uikit", "crop": (24, 538, 642, 800)},
    "plate": {"src": "uikit", "crop": (674, 554, 1004, 646)},
    "battery": {"src": "uikit", "crop": (1040, 602, 1290, 720), "points": {"seg0": (1066, 632), "seg1": (1266, 690)}},
    "slot": {"src": "uikit", "crop": (1320, 554, 1508, 760)},
    "button": {"src": "uikit", "crop": (1540, 610, 1634, 704)},
}
# the window's panes, measured on window7_fixed.png (x0, y0, x1, y1): the stained glass strip and the tall pane under the transom
WIN_PANES = [(22, 22, 120, 55), (22, 61, 120, 210)]
WIN_BOX = [0, 0]
WALL = {"src": "wallpaper.png", "period": (156, 138), "px": 3.9, "area": (150, 160)}
ICON_NAMES = ["amp", "battery", "vowel", "filter", "coil", "echo", "owl", "knob", "treble", "short", "carrier", "fuse"]

def magenta(rgb):
    r, g, b = rgb[..., 0].astype(int), rgb[..., 1].astype(int), rgb[..., 2].astype(int)
    return ((np.minimum(r, b) - g) > 110) | ((np.minimum(r, b) - g > 45) & (b > r * .55) & (b > 90))   # incl. pink edge blends

def fixed(name):
    """The fixed image as RGBA (magenta keyed out) and the scale from source pixels to fixed pixels."""
    src = Image.open(SRC + name + ".png"); im = Image.open(SRC + name + "_fixed.png").convert("RGBA")
    if name in SQUARE:
        im = im.resize((im.width, round(src.height / SQUARE[name])), Image.NEAREST)
    a = np.asarray(im).copy(); a[..., 3] = np.where(magenta(a[..., :3]) | (a[..., 3] < 128), 0, 255)
    return Image.fromarray(a, "RGBA"), im.width / src.width, im.height / src.height

def main():
    imgs, pts = {}, {}
    cache = {}
    for name, s in SPRITES.items():
        if s["src"] not in cache: cache[s["src"]] = fixed(s["src"])
        im, fx, fy = cache[s["src"]]
        if "crop" in s:
            x0, y0, x1, y1 = s["crop"]; box = (round(x0 * fx), round(y0 * fy), round(x1 * fx), round(y1 * fy))
        else:
            box = im.getbbox()
        if name == "window":
            from scipy import ndimage
            src_im = Image.open(SRC + "window7_fixed.png").convert("RGB"); arr = np.asarray(src_im).astype(int)
            mag = magenta(arr); lab, _ = ndimage.label(mag); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
            keep = ~np.isin(lab, list(edge)); im = Image.fromarray(np.dstack([arr.astype(np.uint8), keep.astype(np.uint8) * 255]), "RGBA"); box = im.getbbox()
            WIN_BOX[:] = [box[0], box[1]]
        piece = im.crop(box)
        if "crop" not in s: x0, y0 = box[0] / fx, box[1] / fy
        imgs[name] = piece
        pts[name] = {k: [round(px * fx - box[0]), round(py * fy - box[1])] for k, (px, py) in s.get("points", {}).items()}
    # wallpaper: the median of many repeats (removes the source's uneven edges), one cell per real pixel
    a = np.asarray(Image.open(SRC + WALL["src"]).convert("RGB")).astype(float)
    PX, PY = WALL["period"]; X0, Y0 = WALL["area"]
    tile = np.median(np.stack([a[y:y + PY, x:x + PX] for y in range(Y0, a.shape[0] - PY - 20, PY) for x in range(X0, a.shape[1] - PX - 20, PX)]), 0)
    big = pix.kmeans(tile.reshape(-1, 3)[::3], 24)
    imgs["wall_tile"] = Image.fromarray(pix.mode_shrink(tile, np.ones(tile.shape[:2], bool), round(PX / WALL["px"]), round(PY / WALL["px"]), big), "RGBA")
    # the window glass: which window pixels are the night view (they give their own light, so room light skips them)
    win = np.asarray(imgs["window"]).astype(int); rgb = win[..., :3]
    # the glass is every pane inside the frame: the area the blue night covers, minus whole rows/columns that are wood (the transom bar);
    # lit windows, the stained glass and the beacon inside it count as glass too (they light themselves)
    glass = np.zeros(rgb.shape[:2], bool); ox, oy = WIN_BOX[0], WIN_BOX[1]
    for x0, y0, x1, y1 in WIN_PANES: glass[y0 - oy:y1 - oy, x0 - ox:x1 - ox] = True
    imgs["window_glass"] = Image.fromarray(np.dstack([np.full(glass.shape + (3,), 255, np.uint8), glass.astype(np.uint8) * 255]), "RGBA")
    # what in the window gives off light (for the glow pass): lit building windows, the stained glass sun, the beacon. Kept as a
    # list of light spots (centre, size, colour) the game blooms, plus the night sky area (where the rain falls) as a box.
    from scipy import ndimage
    hsv_hot = (rgb[..., 0] > 170) & (rgb[..., 1] > 120) & (rgb[..., 2] < 140) & glass        # warm yellow / amber
    red = (rgb[..., 0] > 190) & (rgb[..., 1] < 90) & (rgb[..., 2] < 90) & glass                # the beacon
    lights = []
    for m, kind in ((hsv_hot, "warm"), (red, "red")):
        lab, n = ndimage.label(m, np.ones((3, 3)))
        for i, sl in enumerate(ndimage.find_objects(lab)):
            ys, xs = np.where(lab[sl] == i + 1)
            if len(ys) < 2: continue
            lights.append([round(float(xs.mean()) + sl[1].start, 1), round(float(ys.mean()) + sl[0].start, 1), int(len(ys)), kind])
    gy, gx = np.where(glass & (rgb[..., 2] > rgb[..., 0]))
    pts["window_lights"] = lights
    pts["window_panes"] = [[x0 - ox, y0 - oy, x1 - ox, y1 - oy] for x0, y0, x1, y1 in WIN_PANES]
    pts["window_sky"] = [int(gx.min()), int(gy.min()), int(gx.max()) + 1, int(gy.max()) + 1]
    # part icons: full size for the part picker, exactly half (2x2 cells, majority colour) for the bar's slots
    ic, fx, fy = fixed("icons"); ia = np.asarray(ic); al = ia[..., 3] > 0; H, W = al.shape
    for k, name in enumerate(ICON_NAMES):
        cx0, cy0, cx1, cy1 = (k % 4) * W // 4, (k // 4) * H // 3, (k % 4 + 1) * W // 4, (k // 4 + 1) * H // 3
        # keep only the icon itself: the biggest blob in its cell plus anything touching it (bits of the neighbours and stray specks go)
        cell = al[cy0:cy1, cx0:cx1]; lab, n = ndimage.label(cell, np.ones((3, 3))); sizes = ndimage.sum(cell, lab, range(1, n + 1)); big = int(np.argmax(sizes)) + 1
        keep = ndimage.binary_dilation(lab == big, iterations=2) & cell; lab2, _ = ndimage.label(keep, np.ones((3, 3))); keep = np.isin(lab, np.unique(lab[keep & (lab > 0)]))
        ys, xs = np.where(keep); box = (cx0 + xs.min(), cy0 + ys.min(), cx0 + xs.max() + 1, cy0 + ys.max() + 1)
        fa0 = np.asarray(ic).copy(); m = np.zeros(al.shape, bool); m[cy0:cy1, cx0:cx1] = keep; fa0[..., 3] = np.where(m, fa0[..., 3], 0)
        full = Image.fromarray(fa0, "RGBA").crop(box); imgs["iconL_" + name] = full
        fa = np.asarray(full); hw, hh = max(1, fa.shape[1] // 2), max(1, fa.shape[0] // 2)
        pal = np.unique(fa[..., :3][fa[..., 3] > 0].reshape(-1, 3), axis=0).astype(float)
        imgs["icon_" + name] = Image.fromarray(pix.mode_shrink(fa[..., :3].astype(float), fa[..., 3] > 0, hw, hh, pal), "RGBA")
    # interface colours are picked from a palette of the art itself
    sample = np.concatenate([np.asarray(im)[..., :3][np.asarray(im)[..., 3] > 0].reshape(-1, 3) for im in imgs.values() if im.mode == "RGBA"])
    pal = pix.kmeans(sample[::9].astype(float), 56); pal = np.concatenate([pal, np.array(pix.ACCENTS, float)]); pal = np.clip(np.round(pal[np.argsort(pal.mean(1))]), 0, 255).astype(int)
    # pack
    order = sorted(imgs, key=lambda n: -imgs[n].height); AW = 1400; x = y = sh = 0; rects = {}
    for n in order:
        w, h = imgs[n].size
        if x + w > AW: x = 0; y += sh + 1; sh = 0
        rects[n] = [x, y, w, h]; x += w + 1; sh = max(sh, h)
    sheet = Image.new("RGBA", (AW, y + sh + 1), (0, 0, 0, 0))
    for n, (x, y, w, h) in rects.items(): sheet.alpha_composite(imgs[n].convert("RGBA"), (x, y))
    sheet.save(OUT + "atlas.png", optimize=True)
    json.dump({"palette": pal.tolist(), "accents": [list(c) for c in pix.ACCENTS], "rects": rects, "points": pts, "fonts": {}}, open(OUT + "atlas.json", "w"))
    for n in ["radio", "window", "wall_tile", "sb_mid", "bar_left", "bar_mid", "logbox", "plate", "battery", "slot", "iconL_amp", "icon_amp"]: print(n, rects[n][2:])
    print("radio points", pts["radio"]); print("window", pts["window"], "battery", pts["battery"])

main()
