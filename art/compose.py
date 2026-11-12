"""Builds scene.jpg from the art layers: room, night view + tower behind the window glass, window frame, radio + table.
A warm unifying grade is applied (radio gets a slightly stronger pass so it sits in the room's light), then a soft glow.
Run: python3 art/compose.py   (from the repo root)"""
import numpy as np
from PIL import Image, ImageFilter
A = "art/"
def grade(x, tone, desat, warmkeep):
    l = (x[..., 0] * .299 + x[..., 1] * .587 + x[..., 2] * .114)[..., None]
    x = x * (1 - desat) + l * desat
    sh = np.array([.06, .15, .19]); hi = np.array([1.0, .78, .48])
    t = x * (1 - tone) + (sh * (1 - l) + hi * l) * tone
    t = t * (1 - warmkeep) + x * warmkeep
    return np.clip((t - .015) * 1.04 + .02, 0, 1)
def arr(im): return np.asarray(im.convert('RGBA')).astype(float) / 255
def img(a): return Image.fromarray((np.clip(a, 0, 1) * 255).astype('uint8'), 'RGBA')

room = Image.open(A + "room.png").convert('RGBA')
view = Image.open(A + "view.png").convert('RGBA'); view.alpha_composite(Image.open(A + "tower.png"))
win = Image.open(A + "window.png")
k = .56; wx, wy = 150, 70
win_s = win.resize((int(win.width * k), int(win.height * k)), Image.LANCZOS)
gx0, gy0, gx1, gy1 = [int(v * k) for v in (148, 352, 657, 1331)]
gw, gh = gx1 - gx0, gy1 - gy0
sc = max(gw / view.width, gh / view.height)
vs = view.resize((int(view.width * sc), int(view.height * sc)), Image.LANCZOS)
vx = (vs.width - gw) // 2; vs = vs.crop((vx, 0, vx + gw, gh))
bg = room.copy(); bg.alpha_composite(vs, (wx + gx0, wy + gy0)); bg.alpha_composite(win_s, (wx, wy))
bga = arr(bg); bga[..., :3] = grade(bga[..., :3], .16, .10, .25)
radio = arr(Image.open(A + "radio.png")); radio[..., :3] = grade(radio[..., :3], .30, .22, .1)
radio[..., :3] *= .93
scene = img(bga); rl = Image.new('RGBA', scene.size); rl.alpha_composite(img(radio), (230, 0))
scene.alpha_composite(rl)
s = arr(scene)[..., :3]
l = s.mean(2, keepdims=True)
b = np.clip(l - .6, 0, 1) * s
bl = np.asarray(Image.fromarray((b * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(16))) / 255
s = np.clip(s + bl * .7, 0, 1)
Image.fromarray((s * 255).astype('uint8')).save(A + "scene.jpg", quality=88, optimize=True, progressive=True)
print("scene.jpg", Image.open(A + "scene.jpg").size)
