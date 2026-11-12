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

def build_palette(sources, k=64):
    """sources: list of (image path, native size). Samples every native pixel of each, clusters to k colours."""
    samples = []
    for path, size in sources:
        im = Image.open(path).convert("RGB").resize(size, Image.BOX)
        samples.append(np.asarray(im).reshape(-1, 3))
    px = np.concatenate(samples).astype(float)
    pal = kmeans(px, k)
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
