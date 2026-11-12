"""k-centroid downscale: each target pixel takes the main colour of the source pixels it covers (the biggest of two clusters), so
edges stay sharp and colours stay true instead of blurring. Used when a picture's fake pixels can't be recovered exactly.
python3 -I art/pixel/kdown.py SRC OUT WIDTH HEIGHT"""
import sys
import numpy as np
from PIL import Image
src, out, W, H = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
a = np.asarray(Image.open(src).convert("RGB")).astype(float); sh, sw = a.shape[:2]
o = np.zeros((H, W, 3))
for y in range(H):
    for x in range(W):
        c = a[int(y * sh / H):max(int(y * sh / H) + 1, int((y + 1) * sh / H)), int(x * sw / W):max(int(x * sw / W) + 1, int((x + 1) * sw / W))].reshape(-1, 3)
        m = c[[0, -1]].copy()
        for _ in range(4):
            d = ((c[:, None] - m[None]) ** 2).sum(-1); l = d.argmin(1)
            for k in range(2):
                if (l == k).any(): m[k] = c[l == k].mean(0)
        k = np.bincount(l, minlength=2).argmax(); o[y, x] = m[k]
Image.fromarray(np.clip(o.round(), 0, 255).astype(np.uint8)).save(out)
