"""Title glass: Chris's painted picture of the title lit as keys in the radio glass (glass-title-src.jpg).
Makes two versions of the inside of the glass, the same size: glass-lit.png (as painted) and glass-dim.png (every letter and its glow
turned down to a faint engraved letter), and glass.json with a box round each letter in reading order. The game lays the dim one
down and fades each letter's box of the lit one in and out, so letters can switch on, flicker and breathe one at a time.
Run from the repo root: python3 -I art/title/build.py"""
import json
import numpy as np
from PIL import Image
from scipy import ndimage

D = "art/title/"
CROP = (20, 20, 465, 374)          # inside the picture's own brass frame (the radio's bezel frames it in the game)
src = Image.open(D + "glass-title-src.jpg").convert("RGB").crop(CROP)
a = np.asarray(src).astype(float)
hot = (a[..., 0] > 200) & (a[..., 1] > 120)
lab, n = ndimage.label(ndimage.binary_dilation(hot, iterations=3))
boxes = []
for i, s in enumerate(ndimage.find_objects(lab)):
    z = (lab[s] == i + 1).sum()
    if z < 700: continue                                    # specks and edge glints, not letters
    y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
    if x1 - x0 > 120 or y1 - y0 > 120: continue             # the frame, not a letter
    boxes.append([x0, y0, x1, y1])
boxes.sort(key=lambda b: (int((b[1] + b[3]) / 2 // 80), b[0]))   # reading order: by row, then left to right
assert len(boxes) == 13, len(boxes)
soft = ndimage.gaussian_filter(ndimage.binary_dilation(hot, iterations=2).astype(float), 5); soft = np.clip(soft * 1.6, 0, 1)
dim = a * (1 - .85 * soft[..., None]) + np.array([46, 24, 13.0]) * .85 * soft[..., None]   # letters go dark brown, like unlit glass
src.save(D + "glass-lit.png", optimize=True)
Image.fromarray(np.clip(dim, 0, 255).astype(np.uint8)).save(D + "glass-dim.png", optimize=True)
pad = 10
json.dump({"w": src.width, "h": src.height, "letters": "LEXICONSIGNAL", "boxes": [[max(0, x0 - pad), max(0, y0 - pad), min(src.width, x1 + pad), min(src.height, y1 + pad)] for x0, y0, x1, y1 in boxes]}, open(D + "glass.json", "w"))
print(src.size, boxes)
