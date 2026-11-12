"""A full still of the game screen at native 480x270: the lit room (preview.py's light), then the unlit interface bar,
sample letter keys in the radio glass, lit lamps and text. Used to judge layouts before the game code changes.
Usage: python3 -I art/pixel/mock.py OUT.png [scale]"""
import json, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "art/pixel")
import pix
W, H = 480, 270
meta = json.load(open("art/pixel/sprites.json")); pal = np.array(meta["palette"], float); SP = meta["sprites"]
tmp = "/tmp/_room.png"
subprocess.run([sys.executable, "-I", "art/pixel/preview.py", tmp, "1"], check=True)
room = np.asarray(Image.open(tmp).convert("RGB")).astype(float)
def spr(n): return Image.open(f"art/pixel/{n}.png").convert("RGBA")
canvas = Image.fromarray(room.astype("uint8")).convert("RGBA")
def paste(n, x, y): canvas.alpha_composite(spr(n), (int(x), int(y)))
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"; FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
d = ImageDraw.Draw(canvas); d.fontmode = "1"
# ---- letter keys in the glass ----
rx, ry = 172, 14; g0 = SP["radio"]["points"]["glass0"]; g1 = SP["radio"]["points"]["glass1"]
gx0, gy0, gx1, gy1 = rx + g0[0], ry + g0[1], rx + g1[0], ry + g1[1]
tw, th, gap = 23, 19, 3
ox = gx0 + ((gx1 - gx0) - (4 * tw + 3 * gap)) // 2; oy = gy0 + ((gy1 - gy0) - (4 * th + 3 * gap)) // 2
letters = "RATHRNOEVWWAEHOI"; sel = {5, 6, 10}
fk = ImageFont.truetype(FONTB, 14)
for i, ch in enumerate(letters):
    x = ox + (i % 4) * (tw + gap); y = oy + (i // 4) * (th + gap); on = i in sel
    d.rectangle([x, y, x + tw - 1, y + th - 1], fill=(120, 74, 30) if on else (66, 42, 24), outline=(196, 140, 60) if on else (110, 74, 40))
    d.line([x + 1, y + 1, x + tw - 2, y + 1], fill=(160, 104, 52) if not on else (230, 170, 90))
    d.text((x + tw // 2, y + th // 2 + 1), ch, font=fk, anchor="mm", fill=(255, 244, 214) if on else (255, 176, 64))
cs = [(ox + (i % 4) * (tw + gap) + tw // 2, oy + (i // 4) * (th + gap) + th // 2) for i in (5, 6, 10)]
d.line(cs, fill=(255, 226, 150), width=2)
# ---- dial word, meter needle, lamps ----
dx0 = rx + SP["radio"]["points"]["dial0"][0]; dy0 = ry + SP["radio"]["points"]["dial0"][1]
d.text((dx0 + 6, dy0 + 1), "NOW", font=ImageFont.truetype(FONTB, 10), fill=(60, 34, 16))
for t in range(0, 120, 6): d.line([dx0 + 40 + t, dy0 + 10, dx0 + 40 + t, dy0 + (6 if t % 24 else 4)], fill=(90, 60, 30))
d.line([dx0 + 88, dy0 + 2, dx0 + 88, dy0 + 11], fill=(200, 40, 30))
m = SP["radio"]["points"]["meter"]; mx, my = rx + m[0], ry + m[1] + 6
d.line([mx, my, mx + 8, my - 9], fill=(200, 40, 30)); d.point((mx, my), fill=(40, 24, 12))
for k in range(6):
    p = SP["radio"]["points"][f"lamp{k}"]; lx, ly = rx + p[0], ry + p[1]
    if k < 5: d.ellipse([lx - 6, ly - 6, lx + 6, ly + 6], fill=(255, 200, 80)); d.ellipse([lx - 3, ly - 4, lx + 1, ly], fill=(255, 245, 210))
# ---- bar ----
by = H - 66
x = 0; paste("bar_left", 0, by); x = SP["bar_left"]["w"]
while x < W - SP["bar_right"]["w"]: paste("bar_mid", x, by); x += SP["bar_mid"]["w"]
paste("bar_right", W - SP["bar_right"]["w"], by); paste("bar_clasp", W // 2 - SP["bar_clasp"]["w"] // 2, by)
paste("logbox", 8, by + 5)
fl = ImageFont.truetype(FONT, 8)
for i, line in enumerate(["> TUNED IN. NIGHT 2.", "> SENT NOW  +5", "> SIGNAL 45 OF 57", "> 4 WORDS LEFT"]):
    d.text((16, by + 12 + i * 10), line, font=fl, fill=(70, 40, 18))
paste("plate", 148, by + 9); paste("plate", 148, by + 34)
fp = ImageFont.truetype(FONT, 9)
d.text((148 + 36, by + 19), "SIGNAL 45/57", font=fp, anchor="mm", fill=(70, 40, 18))
d.text((148 + 36, by + 44), "NIGHT 2", font=fp, anchor="mm", fill=(70, 40, 18))
paste("battery", 226, by + 20)
s0 = SP["battery"]["points"]["seg0"]; s1 = SP["battery"]["points"]["seg1"]; sw = (s1[0] - s0[0]) / 6
for k in range(5): d.rectangle([226 + s0[0] + k * sw + 1, by + 20 + s0[1], 226 + s0[0] + (k + 1) * sw - 2, by + 20 + s1[1]], fill=(255, 200, 70))
for k in range(4): paste("slot", 286 + k * 46, by + 11)
out = np.asarray(canvas.convert("RGB")).astype(float)
out = pix.snap(out, pal)
sc = int(sys.argv[2]) if len(sys.argv) > 2 else 3
Image.fromarray(out).resize((W * sc, H * sc), Image.NEAREST).save(sys.argv[1])
