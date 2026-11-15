"""Clean frames made in code (Chris 2026-11-14): the log box from PixelLab's brass panel with a pixel parchment texture, and the
brass bezel round the radio's main screen. Used by build.py."""
import math, random
import numpy as np
from PIL import Image
from scipy import ndimage

def H(h): return [int(h[i:i + 2], 16) for i in (1, 3, 5)]

# ---- the log box -------------------------------------------------------------------------------------------------------
PARCH = {"base": [239, 195, 122], "d1": [235, 187, 109], "d2": [229, 173, 84], "l1": [242, 203, 138], "fib": [221, 159, 67]}
def parch_tile(T=96, seed=11):
    # paper tooth (1-2 px flecks a step darker or lighter) and a few faint fibers, wrapping so the tile repeats without a seam
    r = random.Random(seed); P = {k: np.array(v) for k, v in PARCH.items()}; t = np.zeros((T, T, 3), int); t[:] = P["base"]
    for _ in range(int(T * T * .11)):
        x, y = r.randrange(T), r.randrange(T); c = P["d1"] if r.random() < .65 else (P["l1"] if r.random() < .6 else P["d2"])
        t[y, x] = c
        if r.random() < .4: t[y, (x + 1) % T] = c
    for _ in range(20):
        x, y, l = r.randrange(T), r.randrange(T), r.randint(3, 7)
        for k in range(l): t[y, (x + k) % T] = P["d2"] if k % 3 else P["fib"]
    return t
def logbox(src_png, W=193, Hh=82, m=14):
    """src_png: PixelLab's panel (brass frame, plain middle). Its parchment is recoloured to the old log box's tones, the frame is
    9-sliced to W x Hh from one clean row/column, and the flat middle gets the parchment tile plus a stepped aged edge."""
    im = Image.open(src_png).convert("RGBA"); a = np.asarray(im); ys, xs = np.nonzero(a[..., 3] > 0)
    src = np.asarray(im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))).copy(); h, w = src.shape[:2]
    lum = src[..., :3].astype(float) @ [.3, .59, .11]; lab, _ = ndimage.label((lum > 150) & (src[..., 3] > 0)); inside = lab == lab[h // 2, w // 2]
    ramp = np.array([[221, 159, 67], [229, 173, 84], [235, 187, 109], [239, 195, 122]])
    cols = np.unique(src[inside][:, :3], axis=0); order = np.argsort(cols.astype(float) @ [.3, .59, .11])
    for k, i in enumerate(order):
        sel = inside & (src[..., :3] == cols[i]).all(-1); src[sel, :3] = ramp[min(3, round(k * 3 / max(1, len(cols) - 1)))]
    s = Image.fromarray(src, "RGBA"); o = Image.new("RGBA", (W, Hh)); cx, cy = w // 2, h // 2
    for (a0, b0, a1, b1), d in [((0, 0, m, m), (0, 0)), ((w - m, 0, w, m), (W - m, 0)), ((0, h - m, m, h), (0, Hh - m)), ((w - m, h - m, w, h), (W - m, Hh - m))]: o.alpha_composite(s.crop((a0, b0, a1, b1)), d)
    o.alpha_composite(s.crop((cx, 0, cx + 1, m)).resize((W - 2 * m, m), Image.NEAREST), (m, 0)); o.alpha_composite(s.crop((cx, h - m, cx + 1, h)).resize((W - 2 * m, m), Image.NEAREST), (m, Hh - m))
    o.alpha_composite(s.crop((0, cy, m, cy + 1)).resize((m, Hh - 2 * m), Image.NEAREST), (0, m)); o.alpha_composite(s.crop((w - m, cy, w, cy + 1)).resize((m, Hh - 2 * m), Image.NEAREST), (W - m, m))
    o.alpha_composite(s.crop((cx, cy, cx + 1, cy + 1)).resize((W - 2 * m, Hh - 2 * m), Image.NEAREST), (m, m))
    a = np.asarray(o).copy(); flat = (a[..., :3] == PARCH["base"]).all(-1); ys, xs = np.nonzero(flat)
    dist = ndimage.distance_transform_cdt(flat, metric="chessboard"); t = parch_tile()
    a[ys, xs, :3] = t[ys % 96, xs % 96]; a[flat & (dist <= 2), :3] = PARCH["d2"]
    e = np.nonzero(flat & (dist > 2) & (dist <= 5)); keep = (t[e[0] % 96, e[1] % 96] == PARCH["base"]).all(-1); a[e[0][keep], e[1][keep], :3] = PARCH["d1"]
    return Image.fromarray(a, "RGBA")

# ---- the screen bezel ------------------------------------------------------------------------------------------------
OUT, DEEP, DARK, MID, LIGHT, HI, PALE = H('#120604'), H('#871d06'), H('#ae5c03'), H('#d87205'), H('#f2850b'), H('#efae04'), H('#ebce18')
LIT = [OUT, DARK, HI, PALE, LIGHT, MID, DARK, OUT]; SHAD = [OUT, DEEP, DARK, MID, LIGHT, MID, DEEP, OUT]
def rr_dist(x, y, x0, y0, x1, y1, r):
    cx = min(max(x, x0 + r), x1 - r); cy = min(max(y, y0 + r), y1 - r)
    if (x < x0 + r or x > x1 - r) and (y < y0 + r or y > y1 - r): return r - math.hypot(x - cx, y - cy)
    return min(x - x0, x1 - x, y - y0, y1 - y)
def bezel(a, x0, y0, x1, y1, t=8, r=14, fill=False):
    """Redraw a brass ring round a radio window (x0..x1, y0..y1 inclusive, in radio pixels), lit from the upper left. The glass just
    inside it is cleaned to plain glass (all of it with fill=True). Returns the window's inner rows [y, left, right] (the glass the
    game draws in, rounded at the corners with radius r - t)."""
    from collections import Counter
    glass = Counter(map(tuple, a[160:200, 180:300, :3].reshape(-1, 3))).most_common(1)[0][0]
    ramp = [round(k * 7 / (t - 1)) for k in range(t)]
    rows = {}
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = rr_dist(x + .5, y + .5, x0, y0, x1 + 1, y1 + 1, r)
            if d < 0: continue
            if d >= t:
                rows.setdefault(y, [x, x]); rows[y][1] = x
                if fill or d < t + 7: a[y, x, :3] = glass
                continue
            dl, dt, dr, db = x - x0, y - y0, x1 - x, y1 - y; m_ = min(dl, dt, dr, db)
            lit = (dl == m_ or dt == m_) and not ((dr == m_ and dr < dt) or (db == m_ and db < dl))
            if dt <= r and dr <= r: lit = dt < dr
            if db <= r and dl <= r: lit = dl < db
            a[y, x, :3] = (LIT if lit else SHAD)[ramp[int(d)]]; a[y, x, 3] = 255
    return [[y, l, r_] for y, (l, r_) in sorted(rows.items())]

# ---- one brass for everything (Chris 2026-11-14: the brass varied from piece to piece) -----------------------------------
# Every brass pixel (warm yellow / orange, saturated, not too dark) is swapped for the step of this one ramp that matches its
# brightness, so the bar, plates, frames, case, bezels, clasp and rivet all share the same brass. Wood, parchment, glass and the
# dark outlines are left alone.
BRASS = [H('#6e3304'), H('#9a5306'), H('#c07410'), H('#dc9520'), H('#efb52a'), H('#f8d24a'), H('#fff0a0')]
def unify_brass(im):
    a = np.asarray(im.convert("RGBA")).astype(float); rgb = a[..., :3] / 255; mx = rgb.max(-1); mn = rgb.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0); r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    hue = np.where(mx == r, ((g - b) / np.maximum(mx - mn, 1e-6)) % 6, 0) * 60
    lum = rgb @ [.3, .59, .11]
    brass = (a[..., 3] > 0) & (sat > .68) & (hue > 22) & (hue < 62) & (lum > .28)
    edges = [.36, .46, .56, .66, .76, .86]
    k = np.digitize(lum, edges); out = a.copy(); ramp = np.array(BRASS, float)
    out[brass, :3] = ramp[k[brass]]
    return Image.fromarray(out.astype(np.uint8), "RGBA")

LIT = [OUT, BRASS[2], BRASS[4], BRASS[5], BRASS[4], BRASS[3], BRASS[1], OUT];   # (the screens' bezels; the game lights them a little more than the wood so these don't go gray, Chris 2026-11-14)
SHAD = [OUT, BRASS[0], BRASS[1], BRASS[2], BRASS[3], BRASS[2], BRASS[0], OUT]
