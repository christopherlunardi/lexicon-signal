import asyncio, os, subprocess, shutil, json, base64
from playwright.async_api import async_playwright
W = "/home/claude/lexicon-signal/workshop/img/icecrack-r2"
SC = "/tmp/claude-0/-home-claude/4e5937e9-9393-5c00-aeb4-7f381994b58e/scratchpad/ice"
INIT = """(() => { window.__vt = 0; const SR = 44100, DUR = 40; window.__off = new OfflineAudioContext(2, SR * DUR, SR);
 const mk = () => new Proxy(window.__off, { get(t, k) { if (k === 'currentTime') return window.__vt; if (k === 'state') return 'running'; if (k === 'resume' || k === 'suspend' || k === 'close') return () => Promise.resolve();
   const v = t[k]; return typeof v === 'function' ? v.bind(t) : v; }, set(t, k, v) { t[k] = v; return true; } });
 window.AudioContext = function () { return mk(); }; window.webkitAudioContext = window.AudioContext;
 window.__wav = async (t0, t1) => { const buf = await window.__off.startRendering(), sr = buf.sampleRate, a = Math.floor(t0 * sr), n = Math.floor((t1 - t0) * sr), ch = [buf.getChannelData(0), buf.getChannelData(1)];
   const out = new DataView(new ArrayBuffer(44 + n * 4)), w = (o, s) => { for (let i = 0; i < s.length; i++) out.setUint8(o + i, s.charCodeAt(i)); };
   w(0, 'RIFF'); out.setUint32(4, 36 + n * 4, true); w(8, 'WAVEfmt '); out.setUint32(16, 16, true); out.setUint16(20, 1, true); out.setUint16(22, 2, true); out.setUint32(24, sr, true); out.setUint32(28, sr * 4, true); out.setUint16(32, 4, true); out.setUint16(34, 16, true); w(36, 'data'); out.setUint32(40, n * 4, true);
   for (let i = 0; i < n; i++) for (let c = 0; c < 2; c++) { const v = Math.max(-1, Math.min(1, ch[c][a + i] || 0)); out.setInt16(44 + i * 4 + c * 2, v * 32767, true); }
   let s = ''; const u = new Uint8Array(out.buffer); for (let i = 0; i < u.length; i += 32768) s += String.fromCharCode.apply(null, u.subarray(i, i + 32768)); return btoa(s); }; })();"""
FIND = """window.__find = (ok, pred) => { const nb = (i) => { const r = []; for (let j = 0; j < NN; j++) if (j !== i && Math.abs(j % N - i % N) <= 1 && Math.abs(((j / N) | 0) - ((i / N) | 0)) <= 1) r.push(j); return r; }; let best = null;
  const go = (p) => { if (best) return; if (p.length >= 3 && isValid(p) && pred(p)) { best = [...p]; return; } if (p.length >= 4) return; for (const j of nb(p[p.length - 1])) if (!p.includes(j) && ok(S.grid[j])) { p.push(j); go(p); p.pop(); } };
  for (let i = 0; i < NN && !best; i++) if (ok(S.grid[i])) go([i]); return JSON.stringify(best); }; S.target = 99999; 1"""
MISS = "__find(t => !t.blue && !t.ice && !t.wild && !t.hot, p => true)"
BRK = "__find(t => !t.blue && !t.wild && !t.hot, p => p.some(i => S.grid[i].ice) && !p.every(i => S.grid[i].ice))"
THRU = "__find(t => !t.ice && !t.wild && !t.hot, p => p.some(i => S.grid[i].blue))"
THRU2 = "__find(t => !t.wild && !t.hot, p => p.some(i => S.grid[i].blue))"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        ctx = await b.new_context(viewport={"width":1424,"height":850}); await ctx.add_init_script(INIT)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        d = f"{SC}/snd"; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
        await pg.goto("http://localhost:8768/play.html#test-icelook-icelook-2-step"); await pg.wait_for_timeout(1500)
        await pg.evaluate("__lex('LEXSTEP(60)')"); await pg.evaluate(f"__lex({FIND!r})")
        await pg.evaluate("__lex('Sound.ensure()')")
        bb = await (await pg.query_selector("#screen")).bounding_box(); clip = {"x": bb["x"], "y": bb["y"], "width": bb["width"], "height": bb["height"]}
        st = {"k": 0}; t0 = await pg.evaluate("window.__vt")
        async def fr(n=1, js=None):
            if js: await pg.evaluate(f"__lex({js!r})")
            for _ in range(n):
                await pg.evaluate("LEXSTEP(2); window.__vt += 2 / 60"); await pg.screenshot(path=f"{d}/{st['k']:04d}.png", clip=clip); st["k"] += 1
        async def trace(path, hold, step=5):
            for n in range(1, len(path) + 1): await fr(step, f"S.path = {json.dumps(path[:n])}; S.cursor = {path[n-1]}")
            await fr(hold)
        async def settle(extra=8, cap=200):
            for _ in range(cap):
                await fr(1)
                if await pg.evaluate("__lex('canAct() && !S.blueSpread && !iceFx.length && !blueMove && !flyers.length')"): break
            await fr(extra)
        await fr(10)
        # 1. a word through the blue key with no ice: the small chime (x2)
        await pg.evaluate("__lex('S.grid.forEach(t => t.ice = false)')"); await fr(4)
        m = json.loads(await pg.evaluate(f"__lex({THRU!r})")); print("thru", m)
        await trace(m, 20, 4); await fr(0, "send()"); await settle(10)
        # 2. misses: a key freezes at the end of each turn (cold tink)
        for _ in range(2):
            m = json.loads(await pg.evaluate(f"__lex({MISS!r})")); print("miss", m)
            await trace(m, 6, 3); await fr(0, "send()"); await settle(6)
        await fr(10, "{ const b = blueAt(); blueNb(b).filter(j => !S.grid[j].ice && !S.grid[j].hot && !S.grid[j].wild).slice(0, 2).forEach(j => { S.grid[j].ice = true; S.grid[j].iceT = frame; }); }")
        # 3. through the blue key with ice: the burst and the rising run
        m = json.loads(await pg.evaluate(f"__lex({THRU2!r})")); print("thru2", m)
        await trace(m, 30, 4); await fr(0, "send()"); await settle(14)
        # 4. rebuild ice, then a word on the ice without the blue key: crack, the sad drop, the key reforms
        await fr(10, "{ const b = blueAt(); blueNb(b).filter(j => !S.grid[j].ice && !S.grid[j].hot && !S.grid[j].wild).slice(0, 4).forEach(j => { S.grid[j].ice = true; S.grid[j].iceT = frame; }); }")
        m = json.loads(await pg.evaluate(f"__lex({BRK!r})")); print("break", m)
        await trace(m, 34, 4); await fr(0, "send()"); await settle(30)
        t1 = await pg.evaluate("window.__vt"); print("frames", st["k"], "secs", t1 - t0)
        wav = await pg.evaluate(f"window.__wav({t0}, {t1})"); open(f"{d}.wav", "wb").write(base64.b64decode(wav))
        subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate","30","-i",f"{d}/%04d.png","-i",f"{d}.wav","-vf","scale=1280:-2","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",f"{W}/icecrack-sound.mp4"])
        print(errs); await b.close()
asyncio.run(main())
