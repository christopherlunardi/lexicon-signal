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
from PIL import Image, ImageDraw
sys.path.insert(0, "art/pixel")
import pix

SRC = "art/pixel/src/"
OUT = "art/pixel/"
SQUARE = {"uikit": 3.197, "radio5": 3.236}     # sources whose fixed rows need evening out: real pixel size in source px (both axes)
SPRITES = {
    # the window (2026-11-12, Chris picked design 7 of 9: tall, stained glass across the top). Its source had no recoverable grid, so
    # window7_fixed.png is a k-centroid downscale (art/pixel/kdown.py) to 141x233: same width as before, taller.
    "window": {"src": "window7", "points": {"beacon": (174.5, 210.5)}},
    # the radio (2026-11-12): redrawn with a bigger glass for a 5x5 grid (radio5); the 4x4 one ("radio" source) is kept for reference
    "radio": {"src": "radio5", "points": {
        "glass0": (429, 222), "glass1": (1171, 714), "dial0": (412, 106), "dial1": (1163, 174), "meter": (1440, 140), "meterR": (1460, 140),
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
    # the brass plate's top rivets came out smeared (Chris 2026-11-13): each side's top rivet becomes a copy of the clean bottom one
    # (after the palette is taken, so the interface colours stay as they were)
    pa = np.asarray(imgs["plate"]).copy(); pw_ = pa.shape[1]
    for c0, c1 in [(3, 10), (pw_ - 10, pw_ - 4)]: pa[5:12, c0:c1] = pa[16:23, c0:c1]   # rows 5-11: row 12 and below repeat when a plate is stretched taller
    imgs["plate"] = Image.fromarray(pa, "RGBA")
    # the Vowel Antenna was redrawn on its own (2026-11-13, Chris: the old one was crooked and too skinny): vowel_icon.png is the
    # ChatGPT picture, vowel_icon_fixed.png its k-centroid downscale (kdown.py) to 35x62; magenta is keyed out here (after the palette is taken, so the interface colours stay as they were)
    vi = np.asarray(Image.open(SRC + "vowel_icon_fixed.png").convert("RGBA")).copy(); mg = (vi[..., 0] > 170) & (vi[..., 1] < 110) & (vi[..., 2] > 170); vi[..., 3] = np.where(mg, 0, 255)
    full = Image.fromarray(vi, "RGBA"); imgs["iconL_vowel"] = full; fa = np.asarray(full); hw, hh = max(1, fa.shape[1] // 2), max(1, fa.shape[0] // 2)
    vpal = np.unique(fa[..., :3][fa[..., 3] > 0].reshape(-1, 3), axis=0).astype(float)
    imgs["icon_vowel"] = Image.fromarray(pix.mode_shrink(fa[..., :3].astype(float), fa[..., 3] > 0, hw, hh, vpal), "RGBA")
    # the Gold Key (rare part, 2026-11-13): src/gold_icon_fixed.png when it's drawn; until then a stand-in made here: a gold key cap
    # with a dark question mark, so the game has something to show
    import os
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
