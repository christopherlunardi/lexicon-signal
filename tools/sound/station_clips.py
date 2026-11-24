"""Renders the Workshop station clips: each station with three words played over it, and a tour of all six with retunes."""
import json, subprocess, os, sys
import pathlib
S = os.environ.get("OUT", str(pathlib.Path(__file__).parent))   # where the wavs go. Run with the local server on :8771 (python3 -m http.server 8771 in the repo)
def word(t0, n, big=False):
    e = {}; t = t0
    for k in range(1, n + 1): e[round(t, 2)] = f"Sound.blip({k})"; t += .35
    e[round(t - .15, 2)] = "Sound.lock()"; t += .6
    e[round(t, 2)] = f"Sound.send({str(big).lower()})"; t += 1
    e[round(t, 2)] = f"Sound.beacon({str(big).lower()})"; t += .3
    for k in range(6): e[round(t + k * .08, 2)] = f"Sound.cell({.1 + k * .1:.2f})"
    t += 1.2
    for k in range(1, n + 1): e[round(t, 2)] = f"Sound.tlStep(0,{k},true)"; t += .18
    e[round(t + .2, 2)] = "Sound.tlRoll(true)"; t += .7
    e[round(t, 2)] = f"Sound.tlStep(2,{n+1},true)"; t += .4
    e[round(t, 2)] = f"Sound.tlStep(4,{n+2},true)"; t += .5
    e[round(t, 2)] = "Sound.tlTotal(true)"
    return e
def station_events():
    e = {}; e.update(word(3, 4)); e.update(word(12, 6, True)); e.update(word(21, 5))
    e[29.5] = "Sound.full()"; e[30.5] = "Sound.clear()"; return e
def tour_events():
    e = {}
    for k in range(6):
        b = k * 14; e.update(word(b + 3, 4 + k % 3, k % 2 == 1))
        if k < 5: e[b + 13.0] = "Sound.dial(); Sound.next(1.05)"
    return e
jobs = []
for i in range(6):
    env = dict(os.environ, EV=json.dumps({str(k): v for k, v in station_events().items()}), NOFX="")
    env.pop("NOFX")
    jobs.append(subprocess.Popen(["node", str(pathlib.Path(__file__).parent / "render.js"), f"test-title-stn-{i}", f"st{i}.wav", "34", "titleSkip = true;"], cwd=S, env=env, stdout=subprocess.DEVNULL))
env = dict(os.environ, EV=json.dumps({str(k): v for k, v in tour_events().items()}))
jobs.append(subprocess.Popen(["node", str(pathlib.Path(__file__).parent / "render.js"), "test-title-stn-0-1-2-3-4-5", "tour.wav", "84", "titleSkip = true;"], cwd=S, env=env, stdout=subprocess.DEVNULL))
for j in jobs: j.wait()
print("rendered")
