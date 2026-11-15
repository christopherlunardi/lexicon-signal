"""Builds every pixel-art sprite for the game from the art in art/pixel/src/.

ChatGPT's "pixel art" is a big image of fake pixels of uneven size. Each source was run once through a pixel-grid fixer, which
recovered its real pixel grid; that result is saved next to it as NAME_fixed.png. Sprites are cut from the fixed images at exactly
their own pixel size: never resized, never forced into a small palette, so every pixel stays clean. (The interface kit came back
with tall pixels, so its rows are evened out to square pixels first.)

Crops and points below are written in the ORIGINAL source's pixels (easy to measure on the big image) and converted to the fixed
image's pixels. Outputs: atlas.png + atlas.json (palette for interface colours, sprite rectangles, marked points).
Run from the repo root: python3 -I art/pixel/build.py"""
import json, os, sys, hashlib
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
sys.path.insert(0, "art/pixel")
import pix

ROOT_ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..") + "/"
SRC = "art/pixel/src/"
OUT = "art/pixel/"
SQUARE = {"uikit": 3.197, "radio5": 3.236}     # sources whose fixed rows need evening out: real pixel size in source px (both axes)
SPRITES = {
    # the window (2026-11-12, Chris picked design 7 of 9: tall, stained glass across the top). Its source had no recoverable grid, so
    # window7_fixed.png is a k-centroid downscale (art/pixel/kdown.py) to 141x233: same width as before, taller.
    "window": {"src": "window7", "points": {"beacon": (174.5, 210.5)}},
    # the radio (2026-11-12): redrawn with a bigger glass for a 5x5 grid (radio5); the 4x4 one ("radio" source) is kept for reference
    "radio": {"src": "radio5", "points": {
        "glass0": (429, 222), "glass1": (1171, 714), "dial0": (397, 96), "dial1": (1208, 171), "meter": (1440, 140), "meterR": (1460, 140),
        "lamp0": (559, 797), "lamp1": (655, 797), "lamp2": (751, 797), "lamp3": (847, 797), "lamp4": (943, 797), "lamp5": (1041, 797),
        "knobL": (276, 791), "knobR": (1328, 790)}},
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
SASH_Y = 133   # top row of the sash bar across the tall pane (window7_fixed pixels); the bar is as tall as the transom (6 rows)
WIN_BOX = [0, 0]
WALL = {"src": "wallpaper.png", "period": (156, 138), "px": 3.9, "area": (150, 160)}
ICON_NAMES = ["amp", "battery", "vowel", "filter", "coil", "echo", "owl", "knob", "treble", "short", "carrier", "fuse"]

def magenta(rgb):
    r, g, b = rgb[..., 0].astype(int), rgb[..., 1].astype(int), rgb[..., 2].astype(int)
    return ((np.minimum(r, b) - g) > 110) | ((np.minimum(r, b) - g > 45) & (b > r * .55) & (b > 90))   # incl. pink edge blends

def fixed(name):
    """The fixed image as RGBA (magenta keyed out) and the scale from source pixels to fixed pixels."""
    src = Image.open(SRC + name + ".png")
    # NAME_k.png (2026-11-13, Chris: "bad pixelization"): the original art shrunk once with our k-centroid downscale (kdown.py) straight
    # to its true size. Cleaner than the grid-recovered _fixed.png, whose evened-out rows doubled every few lines. Used where it exists.
    if os.path.exists(SRC + name + "_k.png"): im = Image.open(SRC + name + "_k.png").convert("RGBA")
    else: im = Image.open(SRC + name + "_fixed.png").convert("RGBA")
    if name in SQUARE and not os.path.exists(SRC + name + "_k.png"):
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
        if name == "radio" and s["src"] == "radio":
            # the round meter top right did nothing (Chris 2026-11-12): wood over it, a mirror of the same spot on the left of the
            # cabinet (the cabinet is symmetrical), so the space is clean and free for something better later
            ra = np.asarray(piece).copy(); x0, y0, x1, y1 = 308, 5, 364, 60; rw_ = ra.shape[1]
            ra[y0:y1, x0:x1] = ra[y0:y1, rw_ - x1:rw_ - x0][:, ::-1]
            ra[y0:54, 298:313] = ra[y0:54, 318:333]   # the meter's left rim: plain wood from just beside it
            piece = Image.fromarray(ra, "RGBA")
        imgs[name] = piece
        pts[name] = {k: [round(px * fx - box[0]), round(py * fy - box[1])] for k, (px, py) in s.get("points", {}).items()}
    # wallpaper: the median of many repeats (removes the source's uneven edges), one cell per real pixel
    a = np.asarray(Image.open(SRC + WALL["src"]).convert("RGB")).astype(float)
    PX, PY = WALL["period"]; X0, Y0 = WALL["area"]
    tile = np.median(np.stack([a[y:y + PY, x:x + PX] for y in range(Y0, a.shape[0] - PY - 20, PY) for x in range(X0, a.shape[1] - PX - 20, PX)]), 0)
    big = pix.kmeans(tile.reshape(-1, 3)[::3], 24)
    imgs["wall_tile"] = Image.fromarray(pix.mode_shrink(tile, np.ones(tile.shape[:2], bool), round(PX / WALL["px"]), round(PY / WALL["px"]), big), "RGBA")
    # the night: Chris liked option 2's teal-green sky (2026-11-12). Every blue pixel of the tall pane (sky, buildings, tower) is
    # recoloured by brightness rank to option 2's teal night, sampled from the design sheet, so darks stay dark and lights stay light.
    ref = np.asarray(Image.open(SRC + "windows9.png").convert("RGB")).astype(float)[60:440, 400:625]
    tl = ref[(ref[..., 1] > ref[..., 0] + 8) & (ref[..., 2] > ref[..., 0])]; tl = tl[np.argsort(tl @ [.3, .59, .11])]
    wa = np.asarray(imgs["window"]).copy(); wr = wa[..., :3].astype(float); ox, oy = WIN_BOX
    for x0, y0, x1, y1 in WIN_PANES:   # both panes (the stained glass strip's blue corner pieces too)
        sub = wr[y0 - oy:y1 - oy, x0 - ox:x1 - ox]; blue = (sub[..., 2] > sub[..., 0] + 8) & (sub[..., 2] >= sub[..., 1])
        if not blue.any(): continue
        lum = sub[blue] @ [.3, .59, .11]; rank = np.argsort(np.argsort(lum)) / max(1, len(lum) - 1)
        q = (rank * (len(tl) - 1)).astype(int); sub[blue] = np.array([tl[max(0, i - 40):i + 41].mean(0) for i in q])
        wr[y0 - oy:y1 - oy, x0 - ox:x1 - ox] = sub
    wa[..., :3] = np.clip(wr.round(), 0, 255).astype(np.uint8)
    # a sash: the wooden bar under the stained glass is copied across the middle of the tall pane, so it reads as a window that opens
    # (Chris 2026-11-12). The pane becomes two (WIN_PANES lists them).
    ty0, ty1 = WIN_PANES[0][3], WIN_PANES[1][1]; my = SASH_Y
    wa[my - oy:my - oy + (ty1 - ty0), :] = np.where(wa[ty0 - oy:ty1 - oy, :, 3:4] > 0, wa[ty0 - oy:ty1 - oy, :], wa[my - oy:my - oy + (ty1 - ty0), :])
    imgs["window"] = Image.fromarray(wa, "RGBA")
    # the window glass: which window pixels are the night view (they give their own light, so room light skips them)
    win = np.asarray(imgs["window"]).astype(int); rgb = win[..., :3]
    # the glass is every pane inside the frame: the area the blue night covers, minus whole rows/columns that are wood (the transom bar);
    # lit windows, the stained glass and the beacon inside it count as glass too (they light themselves)
    glass = np.zeros(rgb.shape[:2], bool); ox, oy = WIN_BOX[0], WIN_BOX[1]
    for x0, y0, x1, y1 in WIN_PANES: glass[y0 - oy:y1 - oy, x0 - ox:x1 - ox] = True
    glass[SASH_Y - oy:SASH_Y - oy + (WIN_PANES[1][1] - WIN_PANES[0][3]), :] = False
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
    sh = WIN_PANES[1][1] - WIN_PANES[0][3]; P2 = [WIN_PANES[0], (WIN_PANES[1][0], WIN_PANES[1][1], WIN_PANES[1][2], SASH_Y), (WIN_PANES[1][0], SASH_Y + sh, WIN_PANES[1][2], WIN_PANES[1][3])]
    pts["window_panes"] = [[x0 - ox, y0 - oy, x1 - ox, y1 - oy] for x0, y0, x1, y1 in P2]
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
    # One rivet everywhere (Chris 2026-11-13: the painted rivets didn't match from piece to piece): a clean 7x7 brass rivet with a dark
    # rim, a bright top-left, a shaded bottom-right and a screw slot, stamped over every painted one at its frame corner (centres measured
    # per piece, kept symmetric). Also saved as its own sprite "rivet" for anything drawn in code. After the palette is taken.
    RIV = ["..OOO..", ".OHHBO.", "OHHBBSO", "OKKKKKO", "OBBBSSO", ".OSSSO.", "..OOO.."]
    RC = {"O": (42, 12, 2, 255), "H": (255, 242, 160, 255), "B": (246, 178, 28, 255), "S": (176, 106, 4, 255), "K": (58, 20, 4, 255)}
    rivet = Image.new("RGBA", (7, 7), (0, 0, 0, 0))
    for j, row in enumerate(RIV):
        for i, c in enumerate(row):
            if c in RC: rivet.putpixel((i, j), RC[c])
    # the rivet on the Pixel Bench (Chris 2026-11-14): his painted one (src/bench/rivet.png, exactly as painted) replaces it
    os.makedirs(ROOT_ART + "bench/img", exist_ok=True); rivet.save(ROOT_ART + "bench/img/rivet.png")
    if os.path.exists(SRC + "bench/rivet.png"): rivet = Image.open(SRC + "bench/rivet.png").convert("RGBA")
    # the plate's old rivets are painted out with its plain face first (they were smeared and uneven)
    pa = np.asarray(imgs["plate"]).copy(); pw_ = pa.shape[1]
    for c0, c1 in [(3, 10), (pw_ - 11, pw_ - 4)]:
        for r in list(range(4, 13)) + list(range(16, 23)): pa[r, c0:c1] = pa[13, c0:c1]
    # the face's bottom edge: a dark line like the one under the top rim, so the bottom rim doesn't run into the face (Chris 2026-11-13)
    pa[22, 3:pw_ - 3] = pa[3, 3:pw_ - 3]
    # and down each side, so the side rims read apart from the face too
    # (the sides stay as drawn: lines painted down them made the rounded ends ragged, Chris 2026-11-13)
    # the log box's outer edge, top and bottom: clean even bands instead of speckled pixels (Chris: it looked hairy)
    lb = np.asarray(imgs["logbox"]).copy(); lw_, lh_ = lb.shape[1], lb.shape[0]
    for r in (0, 1, 2, lh_ - 3, lh_ - 2, lh_ - 1):
        seg = lb[r, 14:lw_ - 14]; op = seg[..., 3] > 0
        if op.sum(): lb[r, 14:lw_ - 14, :3] = np.median(seg[op][:, :3], axis=0).astype(np.uint8); lb[r, 14:lw_ - 14, 3] = 255 if op.mean() > .5 else 0
    lb[0, 14:lw_ - 14] = lb[1, 14:lw_ - 14]   # the thin darker wood line on top takes the lighter wood under it (Chris 2026-11-13)
    lb[lh_ - 1, 14:lw_ - 14, 3] = 0           # (the very bottom row was a leftover purple edge from the keyed background)
    imgs["logbox"] = Image.fromarray(lb, "RGBA")
    imgs["plate"] = Image.fromarray(pa, "RGBA"); imgs["plate_bare"] = imgs["plate"].copy()   # (bare: for short plates, which get one rivet each end)
    # (on the painted frames they sit right over the painted ones so none shows from under them; the plate's were painted out, so
    # its rivets sit a pixel inside the brass)
    RIVETS = {"plate": [(8, 8), (93, 8), (8, 17), (93, 17)], "logbox": [(8, 7), (184, 7), (8, 71), (184, 71)],
              "slot": [(6, 6), (52, 6), (6, 56), (52, 56)], "bar_left": [(11, 13), (11, 81)], "bar_right": [(26, 12), (26, 81)],
              "tplate": [(9, 8), (88, 8), (9, 24), (88, 24)], "tplate_lit": [(9, 8), (88, 8), (9, 24), (88, 24)]}
    # the Vowel Antenna was redrawn on its own (2026-11-13, Chris: the old one was crooked and too skinny): vowel_icon.png is the
    # ChatGPT picture, vowel_icon_fixed.png its k-centroid downscale (kdown.py) to 35x62; magenta is keyed out here (after the palette is taken, so the interface colours stay as they were)
    vi = np.asarray(Image.open(SRC + "vowel_icon_fixed.png").convert("RGBA")).copy(); mg = (vi[..., 0] > 170) & (vi[..., 1] < 110) & (vi[..., 2] > 170); vi[..., 3] = np.where(mg, 0, 255)
    full = Image.fromarray(vi, "RGBA"); imgs["iconL_vowel"] = full; fa = np.asarray(full); hw, hh = max(1, fa.shape[1] // 2), max(1, fa.shape[0] // 2)
    vpal = np.unique(fa[..., :3][fa[..., 3] > 0].reshape(-1, 3), axis=0).astype(float)
    imgs["icon_vowel"] = Image.fromarray(pix.mode_shrink(fa[..., :3].astype(float), fa[..., 3] > 0, hw, hh, vpal), "RGBA")
    # the Gold Key (rare part, 2026-11-13): src/gold_icon_fixed.png when it's drawn; until then a stand-in made here: a gold key cap
    # with a dark question mark, so the game has something to show
    if os.path.exists(SRC + "gold_icon_fixed.png"):
        gi = np.asarray(Image.open(SRC + "gold_icon_fixed.png").convert("RGBA")).copy(); mg = (gi[..., 0] > 170) & (gi[..., 1] < 110) & (gi[..., 2] > 170); gi[..., 3] = np.where(mg, 0, 255)
        gold = Image.fromarray(gi, "RGBA")
    else:
        gold = Image.new("RGBA", (40, 46), (0, 0, 0, 0)); d = ImageDraw.Draw(gold)
        d.rounded_rectangle((1, 1, 38, 44), 6, fill=(92, 56, 12, 255)); d.rounded_rectangle((3, 3, 36, 38), 5, fill=(214, 160, 40, 255)); d.rounded_rectangle((5, 5, 34, 20), 4, fill=(246, 206, 92, 255))
        q = ["01110", "10001", "00001", "00010", "00100", "00000", "00100"]
        for r, row in enumerate(q):
            for c, on in enumerate(row):
                if on == "1": d.rectangle((10 + c * 4, 7 + r * 4, 13 + c * 4, 10 + r * 4), fill=(60, 30, 6, 255))
    imgs["iconL_gold"] = gold; fa = np.asarray(gold); hw, hh = max(1, fa.shape[1] // 2), max(1, fa.shape[0] // 2)
    gpal = np.unique(fa[..., :3][fa[..., 3] > 0].reshape(-1, 3), axis=0).astype(float)
    imgs["icon_gold"] = Image.fromarray(pix.mode_shrink(fa[..., :3].astype(float), fa[..., 3] > 0, hw, hh, gpal), "RGBA")
    # the Center Tap (gold part, 2026-11-14): src/tap_icon.png (ChatGPT) shrunk by k-centroid to its native grid (152 px square),
    # cropped to the object and shrunk again to 46x60 (kdown.py) as src/tap_icon_fixed.png; magenta keyed out like the Gold Key
    ti = np.asarray(Image.open(SRC + "tap_icon_fixed.png").convert("RGBA")).copy(); mg = (ti[..., 0] > 170) & (ti[..., 1] < 110) & (ti[..., 2] > 170); ti[..., 3] = np.where(mg, 0, 255)
    imgs["iconL_tap"] = Image.fromarray(ti, "RGBA"); fa = ti; hw, hh = max(1, fa.shape[1] // 2), max(1, fa.shape[0] // 2)
    tpal = np.unique(fa[..., :3][fa[..., 3] > 0].reshape(-1, 3), axis=0).astype(float)
    imgs["icon_tap"] = Image.fromarray(pix.mode_shrink(fa[..., :3].astype(float), fa[..., 3] > 0, hw, hh, tpal), "RGBA")
    # the title screen's console (2026-11-13, Chris's art src/title_console.png): a wooden console panel and two brass button plates
    # (unlit, lit), k-centroid shrunk to *_fixed.png; magenta keyed out. Taken after the palette so the interface colours don't move.
    for nm, fn in (("tpanel", "title_panel_fixed.png"), ("tplate", "title_plate_fixed.png"), ("tplate_lit", "title_plate_lit_fixed.png")):
        ti = np.asarray(Image.open(SRC + fn).convert("RGBA")).copy(); r_, g_, b_ = ti[..., 0].astype(int), ti[..., 1].astype(int), ti[..., 2].astype(int)
        mg = (b_ > 120) & (r_ > 120) & (g_ < r_ - 60) & (g_ < b_ - 60); ti[..., 3] = np.where(mg, 0, 255); imgs[nm] = Image.fromarray(ti, "RGBA")
    # the melter and its reward, the molten upgrade (2026-11-13, Chris's art src/melter_icon.png, molten_icon.png), k-centroid shrunk
    # the title cabinet under the radio (2026-11-13, src/title_cabinet.png): its top with the empty name panel, and a drawer row that repeats down
    for nm, fn in (("iconL_melter", "melter_icon_fixed.png"), ("iconL_molten", "molten_icon_fixed.png"), ("cab_top", "cab_top_fixed.png"), ("cab_row", "cab_row_fixed.png"), ("big_melter", "melter_big_fixed.png"), ("big_molten", "molten_big_fixed.png")):
        ti = np.asarray(Image.open(SRC + fn).convert("RGBA")).copy(); r_, g_, b_ = ti[..., 0].astype(int), ti[..., 1].astype(int), ti[..., 2].astype(int)
        mg = (b_ > 120) & (r_ > 120) & (g_ < r_ - 60) & (g_ < b_ - 60); ti[..., 3] = np.where(mg, 0, 255); imgs[nm] = Image.fromarray(ti, "RGBA")
    # plain wood where the title buttons sit (Chris 2026-11-14: no outlined panel round them): the panel's ring and the face around it,
    # between the two pilasters, are filled with the panel's own inside wood (its rows stacked, shifted along so the grain doesn't repeat); nothing else changes
    ct = np.asarray(imgs["cab_top"]).copy(); IX0, IX1, IY0, IY1 = 52, 504, 40, 62; FX0, FX1, FY0, FY1 = 38, 518, 31, 75
    def refl(v, a, b): n = b - a; k = (v - a) % (2 * n); return a + (k if k < n else 2 * n - 1 - k)
    src_ = ct.copy()
    for yy in range(FY0, FY1):
        n_ = IY1 - IY0; sy = IY0 + (yy - FY0) % n_; sh_ = 173 * ((yy - FY0) // n_)
        for xx in range(FX0, FX1): ct[yy, xx] = src_[sy, refl(xx + sh_, IX0, IX1)]
    imgs["cab_top"] = Image.fromarray(ct, "RGBA")
    # The Pixel Bench (Chris 2026-11-13, art/bench/: his pixel touch-up page): the framed pieces as they are under the rivets go
    # to art/bench/img/ for him to paint on, and a piece he sends back (saved as src/bench/NAME.png, exactly as painted) replaces
    # the cut one here, before the rivets go on.
    BENCH = {"logbox": "The log box / sheets frame (corners are kept; the middle repeats)", "plate": "Brass plate (bare: no rivets)",
             "slot": "Part slot / part case frame", "bar_left": "The bar: left end", "bar_mid": "The bar: the middle that repeats",
             "bar_right": "The bar: right end", "tplate": "Title menu plate", "tplate_lit": "Title menu plate (lit)"}
    os.makedirs(ROOT_ART + "bench/img", exist_ok=True); man = []
    for nm, lab in BENCH.items():
        fix = SRC + "bench/" + nm + ".png"
        if os.path.exists(fix):
            imgs[nm] = Image.open(fix).convert("RGBA")
            if nm == "plate": imgs["plate_bare"] = imgs["plate"].copy()
        im_ = imgs["plate_bare"] if nm == "plate" else imgs[nm]; im_.save(ROOT_ART + "bench/img/" + nm + ".png")
        man.append({"file": "img/" + nm + ".png", "group": "Done: in the game" if os.path.exists(fix) else "To do: frames under the rivets", "label": lab + (" (rivets go at " + ", ".join(f"{x},{y}" for x, y in RIVETS.get(nm, [])) + ")" if nm in RIVETS else ""), "w": im_.width, "h": im_.height, "key": nm})
    # one piece at a time (Chris 2026-11-13): the bench shows only the next one to do; when he sends it, the next goes up
    todo = [m for m in man if not m["group"].startswith("Done")]
    if not os.path.exists(SRC + "bench/rivet.png"):   # the rivet goes up first (Chris 2026-11-14)
        todo = [{"file": "img/rivet.png", "group": "To do: the rivet used everywhere", "label": "The rivet (7x7, used on every frame and plate)", "name": "rivet"}] + todo
    json.dump(todo[:1], open(ROOT_ART + "bench/manifest.json", "w"), indent=1)
    # The log box (Chris 2026-11-14): PixelLab's brass-only panel (src/logbox_pixellab.png: no wood rim, symmetrical, empty corner
    # pads for our rivets) with a pixel parchment texture, made by frames.py. It also frames every big parchment panel.
    # The radio's screen bezel is redrawn clean in code (frames.bezel), the rest of the radio untouched.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import frames
    # the brass plate (goal / night plates, name plates, title and prompt plates...): PixelLab's plain brass rim round a parchment
    # face (src/plate_pixellab.png), no rivets (Chris 2026-11-14: it sits inside the bar's border)
    # (src/plate_brass.png: PixelLab's plate, src/pending/plate_pixellab.png, cropped, its rim rows evened out and its parchment face
    # made solid brass, Chris: plates are brass, the paper is for the log and panels)
    if os.path.exists(SRC + "plate_brass.png"):
        imgs["plate"] = Image.open(SRC + "plate_brass.png").convert("RGBA"); imgs["plate_bare"] = imgs["plate"].copy(); RIVETS["plate"] = [(7, 7), (94, 7), (7, 18), (94, 18)]   # (inside the rim, two at each end)
    # the part slot / part case frame (Chris 2026-11-14): PixelLab's brass case (src/slot_pixellab.png, brass only, empty corner pads)
    # fitted to the slot's 59x64: corners kept, the even middle stretched from one row / column
    if os.path.exists(SRC + "slot_pixellab.png"):
        sp = Image.open(SRC + "slot_pixellab.png").convert("RGBA"); sa = np.asarray(sp); ys_, xs_ = np.nonzero(sa[..., 3] > 0)
        sp = sp.crop((xs_.min(), ys_.min(), xs_.max() + 1, ys_.max() + 1)); sw_, sh_ = sp.size; SW, SH, m_ = 59, 64, 12; so = Image.new("RGBA", (SW, SH))
        for (a0, b0), (d0, e0) in [((0, 0), (0, 0)), ((sw_ - m_, 0), (SW - m_, 0)), ((0, sh_ - m_), (0, SH - m_)), ((sw_ - m_, sh_ - m_), (SW - m_, SH - m_))]: so.alpha_composite(sp.crop((a0, b0, a0 + m_, b0 + m_)), (d0, e0))
        cx_, cy_ = sw_ // 2, sh_ // 2
        so.alpha_composite(sp.crop((cx_, 0, cx_ + 1, m_)).resize((SW - 2 * m_, m_), Image.NEAREST), (m_, 0)); so.alpha_composite(sp.crop((cx_, sh_ - m_, cx_ + 1, sh_)).resize((SW - 2 * m_, m_), Image.NEAREST), (m_, SH - m_))
        so.alpha_composite(sp.crop((0, cy_, m_, cy_ + 1)).resize((m_, SH - 2 * m_), Image.NEAREST), (0, m_)); so.alpha_composite(sp.crop((sw_ - m_, cy_, sw_, cy_ + 1)).resize((m_, SH - 2 * m_), Image.NEAREST), (SW - m_, m_))
        so.alpha_composite(sp.crop((cx_, cy_, cx_ + 1, cy_ + 1)).resize((SW - 2 * m_, SH - 2 * m_), Image.NEAREST), (m_, m_))
        # calmer brass (Chris 2026-11-14: too bright, the top especially): on the shared ramp first, then the pale highlights
        # come down to gold and the light gold to mid brass, so the frame reads as warm mid brass like the log box
        so = frames.unify_brass(so); sa_ = np.asarray(so).copy(); B_ = frames.BRASS
        lu_ = sa_[..., :3].astype(float) @ [.3, .59, .11] / 255; warm_ = (sa_[..., 3] > 0) & (sa_[..., 0] >= sa_[..., 1]) & (sa_[..., 1] >= sa_[..., 2])
        hi_ = warm_ & (lu_ > .8); mid_ = warm_ & (lu_ > .66) & ~hi_
        sa_[hi_, :3] = B_[4]; sa_[mid_, :3] = B_[3]
        so = Image.fromarray(sa_, "RGBA")
        imgs["slot"] = so; RIVETS["slot"] = [(5, 5), (53, 5), (5, 58), (53, 58)]
        # the toned frame goes on the Pixel Bench for Chris to redo its corners (2026-11-14); what he sends back is src/bench/slot2.png
        if os.path.exists(SRC + "bench/slot2.png"): imgs["slot"] = Image.open(SRC + "bench/slot2.png").convert("RGBA")
        else:
            so.save(ROOT_ART + "bench/img/slot2.png")
            json.dump([{"file": "img/slot2.png", "group": "To do: frames under the rivets", "label": "Part window, toned brass: the corners (rivets go at 5,5, 53,5, 5,58, 53,58)", "w": so.width, "h": so.height, "key": "slot2"}], open(ROOT_ART + "bench/manifest.json", "w"), indent=1)
    if os.path.exists(SRC + "logbox_pixellab.png"):
        imgs["logbox"] = frames.logbox(SRC + "logbox_pixellab.png"); RIVETS["logbox"] = [(6, 6), (185, 6), (6, 74), (185, 74)]
    # main screen: the ring's inner edge is exactly the glass the game draws in (glass0..glass1); the dial screen above it gets the
    # same ring, a little wider than the old painted one, its inside all glass; the game fills and clips to its rounded rows
    # (the glass is 3 px taller than the painted one so the ring covers the old ring's bottom edge too; the game sizes its keys to it)
    pts["radio"]["glass1"] = [pts["radio"]["glass1"][0], pts["radio"]["glass1"][1] + 3]
    ra = np.asarray(imgs["radio"].convert("RGBA")).copy(); g0, g1 = pts["radio"]["glass0"], pts["radio"]["glass1"]
    frames.bezel(ra, g0[0] - 8, g0[1] - 8, g1[0] - 1 + 8, g1[1] - 1 + 8)
    DIAL_ROWS = frames.bezel(ra, 108, 9, 372, 42, t=7, r=14, fill=True); imgs["radio"] = Image.fromarray(ra, "RGBA")
    pts["radio"]["dial0"] = [min(r_[1] for r_ in DIAL_ROWS), DIAL_ROWS[0][0]]; pts["radio"]["dial1"] = [max(r_[2] for r_ in DIAL_ROWS) + 1, DIAL_ROWS[-1][0] + 1]
    # The bar, redrawn as real pixel art (Chris 2026-11-14): src/bar_panel_pixellab.png is PixelLab's create_ui_asset panel (341x192,
    # palette locked to 21 colours taken from the old bar, the old bar as its style reference), src/bar_panel.png the bar cropped
    # out of it (329x93). Cut here into the same three pieces the game builds the bar from: a left end, a middle that repeats and a
    # right end. Its rivets are its own, so none are stamped on it.
    if os.path.exists(SRC + "bar_panel.png"):
        bp = Image.open(SRC + "bar_panel.png").convert("RGBA"); bw, bh = bp.size
        # PixelLab's brass line has bright and dark patches along it, which repeat as stripes when the middle repeats: the top and
        # bottom bands (rim + brass, 13 rows each) are made from one clean column everywhere past the corners, so they run even
        ba = np.asarray(bp).copy(); col = ba[:, bw // 2].copy(); E = 13
        for x in range(17, bw - 17): ba[:E, x] = col[:E]; ba[bh - E:, x] = col[bh - E:]
        # and the same down the two sides (Chris 2026-11-14: patchy, blended brass at the bar's ends): one clean row everywhere past the corners
        row = ba[bh // 2].copy()
        for y in range(17, bh - 17): ba[y, :E] = row[:E]; ba[y, bw - E:] = row[bw - E:]
        bp = Image.fromarray(ba, "RGBA")
        BAR_RIVETS = [(13, 10), (bw - 13, 10), (13, 80), (bw - 13, 80)]   # where PixelLab painted its own; ours go over them
        ba = np.asarray(bp).copy()
        for cx_, cy_ in BAR_RIVETS:   # a dark round seat that hides PixelLab's rivet; the game's rivet is stamped on it below
            for yy in range(cy_ - 4, cy_ + 5):
                for xx in range(cx_ - 4, cx_ + 5):
                    if (xx - cx_) ** 2 + (yy - cy_) ** 2 <= 20: ba[yy, xx, :3] = (42, 12, 2)
        # the top rail's highlight toned down to the slots' warm gold (Chris 2026-11-14: too pale a yellow for the rest of the brass)
        top_ = ba[:12]; lu_ = top_[..., :3].astype(float) @ [.3, .59, .11] / 255; warm_ = (top_[..., 0] >= top_[..., 1]) & (top_[..., 1] >= top_[..., 2])
        hi_ = warm_ & (lu_ > .8); mid_ = warm_ & (lu_ > .66) & ~hi_; top_[hi_, :3] = frames.BRASS[4]; top_[mid_, :3] = frames.BRASS[3]
        bp = Image.fromarray(ba, "RGBA"); BAR_RIVET_IMG = bp
        imgs["bar_left"] = bp.crop((0, 0, 39, bh)); imgs["bar_right"] = bp.crop((bw - 39, 0, bw, bh)); imgs["bar_mid"] = bp.crop((bw // 2 - 40, 0, bw // 2 + 41, bh))
        RIVETS.pop("bar_left", None); RIVETS.pop("bar_right", None)
    if "BAR_RIVETS" in locals():   # the bar's corner rivets: the game's rivet over PixelLab's (left end: the left pair, right end: the right pair)
        bw_ = BAR_RIVET_IMG.size[0]; RIVETS["bar_left"] = [(x_, y_) for x_, y_ in BAR_RIVETS if x_ < 39]; RIVETS["bar_right"] = [(x_ - (bw_ - 39), y_) for x_, y_ in BAR_RIVETS if x_ >= bw_ - 39]
    for nm, cs in RIVETS.items():
        im_ = imgs[nm].copy()
        for cx, cy in cs: im_.alpha_composite(rivet, (cx - 3, cy - 3))
        imgs[nm] = im_
    imgs["rivet"] = rivet
    # one brass everywhere (Chris 2026-11-14): every brass piece on the shared ramp (frames.BRASS); the lit title plate keeps its glow
    for nm in ["bar_left", "bar_mid", "bar_right", "slot", "plate", "plate_bare", "tplate", "logbox", "bar_clasp", "rivet"]:
        if nm in imgs: imgs[nm] = frames.unify_brass(imgs[nm])
    # the radio's lamp (Chris 2026-11-14): one lamp goes on the Pixel Bench for Chris to paint; what he sends back is src/bench/lamp.png
    if not os.path.exists(SRC + "bench/lamp.png"):
        lx_, ly_ = pts["radio"]["lamp1"]; lc_ = np.asarray(imgs["radio"].crop((lx_ - 17, ly_ - 16, lx_ + 18, ly_ + 19))).copy()   # (the lamp's true middle is half a pixel right of the mark)
        # the wood round it cleared: outside the lamp's dark outline (a circle round its true middle)
        yy_, xx_ = np.mgrid[0:35, 0:35]; seen_ = (yy_ - 17.4) ** 2 + (xx_ - 17.5) ** 2 > 14.2 ** 2
        lc_[seen_, 3] = 0
        Image.fromarray(lc_, "RGBA").save(ROOT_ART + "bench/img/lamp.png")
        json.dump([{"file": "img/lamp.png", "group": "To do: frames under the rivets", "label": "One lamp for under the radio's glass (unlit; the game draws its glow on top). It will be used six times on plain wood", "w": 35, "h": 35, "key": "lamp"}], open(ROOT_ART + "bench/manifest.json", "w"), indent=1)
    # the bar's clasp (Chris 2026-11-14): PixelLab's winged brass piece (src/clasp_wings.png, trimmed to the wings' shape)
    if os.path.exists(SRC + "clasp_wings.png"): imgs["bar_clasp"] = Image.open(SRC + "clasp_wings.png").convert("RGBA")
    # the bar's top-middle clasp on the Pixel Bench (Chris 2026-11-14): what he paints (src/bench/bar_clasp.png) is used exactly as sent
    if os.path.exists(SRC + "bench/bar_clasp.png"): imgs["bar_clasp"] = Image.open(SRC + "bench/bar_clasp.png").convert("RGBA")
    elif not os.path.exists(SRC + "clasp_wings.png"):
        imgs["bar_clasp"].save(ROOT_ART + "bench/img/bar_clasp.png")
        json.dump([{"file": "img/bar_clasp.png", "group": "To do: frames under the rivets", "label": "The bar's clasp (the brass piece at the top middle)", "w": imgs["bar_clasp"].width, "h": imgs["bar_clasp"].height, "key": "bar_clasp"}], open(ROOT_ART + "bench/manifest.json", "w"), indent=1)
    # pack
    order = sorted(imgs, key=lambda n: -imgs[n].height); AW = 1400; x = y = sh = 0; rects = {}
    for n in order:
        w, h = imgs[n].size
        if x + w > AW: x = 0; y += sh + 1; sh = 0
        rects[n] = [x, y, w, h]; x += w + 1; sh = max(sh, h)
    sheet = Image.new("RGBA", (AW, y + sh + 1), (0, 0, 0, 0))
    for n, (x, y, w, h) in rects.items(): sheet.alpha_composite(imgs[n].convert("RGBA"), (x, y))
    sheet.save(OUT + "atlas.png", optimize=True)
    # the dial window's painted shape, row by row (rounded ends): the game fills exactly these pixels so the lit display never
    # pokes past the frame. Each row is the light run through the window's middle, inside the dark outline.
    dial_rows = DIAL_ROWS
    json.dump({"palette": pal.tolist(), "accents": [list(c) for c in pix.ACCENTS], "rects": rects, "points": pts, "dialRows": dial_rows, "fonts": {},
               "v": hashlib.sha1(open(OUT + "atlas.png", "rb").read()).hexdigest()[:10]}, open(OUT + "atlas.json", "w"))   # the picture's version: the game asks for atlas.png?v=<this>, so a phone can't pair a new json with an old cached picture
    for n in ["radio", "window", "wall_tile", "sb_mid", "bar_left", "bar_mid", "logbox", "plate", "battery", "slot", "iconL_amp", "icon_amp"]: print(n, rects[n][2:])
    print("radio points", pts["radio"]); print("window", pts["window"], "battery", pts["battery"])

main()
