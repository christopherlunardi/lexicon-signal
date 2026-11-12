"""Pixel-art pipeline helpers: the master palette, snapping art to it, and the dithered lighting used by the game.
The game draws at a low native size (480x270 for 16:9) and every layer is snapped to one shared palette."""
import json, numpy as np
from PIL import Image

ROOT = "art/pixel/"
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], float) / 16 - .5

def kmeans(px, k, iters=25, seed=1):
    rng = np.random.default_rng(seed)
    c = px[rng.choice(len(px), k, replace=False)].astype(float)
    for _ in range(iters):
        d = ((px[:, None, :] - c[None]) ** 2).sum(-1); lab = d.argmin(1)
        for i in range(k):
            m = px[lab == i]
            if len(m): c[i] = m.mean(0)
    return c

# glow colours kept in the palette no matter what the art contains: key amber, hot white-gold, lamp yellow, beacon reds, cool glass
ACCENTS = [(255, 176, 64), (255, 214, 120), (255, 244, 214), (255, 206, 84), (232, 48, 36), (255, 104, 72), (150, 196, 255), (40, 64, 140)]

def build_palette(sources, k=64):
    """sources: list of (image path, native size). Samples every native pixel of each, clusters to k colours
    (k minus the fixed accent colours), then appends the accents."""
    samples = []
    for path, size in sources:
        im = Image.open(path).convert("RGB").resize(size, Image.BOX)
        samples.append(np.asarray(im).reshape(-1, 3))
    px = np.concatenate(samples).astype(float)
    pal = kmeans(px, k - len(ACCENTS))
    pal = np.concatenate([pal, np.array(ACCENTS, float)])
    pal = pal[np.argsort(pal.mean(1))]  # dark to light
    pal = np.clip(np.round(pal), 0, 255).astype(int)
    json.dump(pal.tolist(), open(ROOT + "palette.json", "w"))
    sw = Image.new("RGB", (k, 1)); sw.putdata([tuple(p) for p in pal]); sw.resize((k * 12, 24), Image.NEAREST).save(ROOT + "palette.png")
    return pal

def palette():
    return np.array(json.load(open(ROOT + "palette.json")), float)

def snap(rgb, pal, dither=0.0):
    """Nearest palette colour per pixel; optional ordered dither strength (0..1, in palette-step units ~ 32 levels)."""
    h, w, _ = rgb.shape
    x = rgb.astype(float)
    if dither:
        t = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w][..., None]
        x = x + t * dither * 48
    d = ((x[:, :, None, :] - pal[None, None]) ** 2).sum(-1)
    return pal[d.argmin(-1)].astype(np.uint8)


def snap_index(rgb, pal):
    """Palette index of the nearest colour per pixel (works in chunks so big images fit in memory)."""
    h, w, _ = rgb.shape; flat = rgb.reshape(-1, 3).astype(float); out = np.empty(len(flat), np.int32)
    for s in range(0, len(flat), 200000):
        d = ((flat[s:s + 200000, None, :] - pal[None]) ** 2).sum(-1); out[s:s + 200000] = d.argmin(1)
    return out.reshape(h, w)

def mode_shrink(rgb, alpha, W, H, pal):
    """Pixel-art-aware shrink: snap the big image to the palette first, then each small pixel takes the most common colour in its
    block (opaque pixels only), so hard edges and flat colours stay crisp instead of being averaged into mud.
    Returns (W,H,4) uint8 RGBA."""
    h, w = alpha.shape; idx = snap_index(rgb, pal)
    ys = (np.arange(h) * H // h); xs = (np.arange(w) * W // w); cell = ys[:, None] * W + xs[None, :]
    k = len(pal); counts = np.zeros((W * H, k), np.int32)
    np.add.at(counts, (cell[alpha], idx[alpha]), 1)
    cov = np.bincount(cell.ravel(), weights=alpha.ravel().astype(float), minlength=W * H) / np.maximum(np.bincount(cell.ravel(), minlength=W * H), 1)
    best = counts.argmax(1); rgbo = pal[best].reshape(H, W, 3).astype(np.uint8); a = (cov.reshape(H, W) > .5).astype(np.uint8) * 255
    return np.dstack([rgbo, a])
