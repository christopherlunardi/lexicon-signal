"""Remove a flat magenta (#FF00FF) background from a generated image and save a transparent PNG.
Usage: python3 -I art/tools/keyout.py IN.png OUT.png
Pixels close to magenta become transparent; edge pixels are softened and have the magenta tint pulled out."""
import sys
import numpy as np
from PIL import Image, ImageFilter

src = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(float)
r, g, b = src[..., 0], src[..., 1], src[..., 2]
m = np.minimum(r, b) - g                      # how magenta a pixel is
alpha = np.clip(1 - (m - 60) / 120, 0, 1)     # >=180 gone, <=60 kept
a8 = Image.fromarray((alpha * 255).astype("uint8")).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
alpha = np.asarray(a8) / 255.0
spill = np.clip(np.minimum(r, b) - g, 0, None) * (1 - alpha)
rgb = src.copy(); rgb[..., 0] -= spill * 0.8; rgb[..., 2] -= spill * 0.8
out = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype("uint8"), "RGBA")
out.save(sys.argv[2])
print(sys.argv[2], out.size, "bbox", out.getbbox())
