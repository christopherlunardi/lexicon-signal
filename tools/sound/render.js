// Renders the game's sound offline (seeded random, a virtual clock) with a scripted list of effects (EV env: {"secs": "js"}).
// Needs the local server on :8771 serving the repo and workshop/play.html built.
// node sndrender.js <hash> <out.wav> <secs> [jsBefore]  : render the game's sound offline (seeded random) with a scripted set of effects
const { chromium } = require('playwright'); const fs = require('fs');
const [hash, out, secs, pre] = process.argv.slice(2); const DUR = +secs;
const INIT = `(() => { let a = 12345; Math.random = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
 window.__vt = 0; const SR = 44100; window.__off = new OfflineAudioContext(2, SR * ${DUR + 2}, SR);
 const mk = () => new Proxy(window.__off, { get(t, k) { if (k === 'currentTime') return window.__vt; if (k === 'state') return 'running'; if (k === 'resume' || k === 'suspend' || k === 'close') return () => Promise.resolve(); const v = t[k]; return typeof v === 'function' ? v.bind(t) : v; }, set(t, k, v) { t[k] = v; return true; } });
 window.AudioContext = function () { return mk(); }; window.webkitAudioContext = window.AudioContext; })();`;
(async () => { const b = await chromium.launch(); const pg = await b.newPage(); await pg.addInitScript(INIT); const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.goto('http://localhost:8771/workshop/play.html#' + hash); await pg.waitForTimeout(1500);
  await pg.evaluate(`__lex('Sound.ensure(); Sound.music(); ${pre || ''}')`);
  // a script of effects: letters climbing, a send, the beacon, tube cells, the count-up, a lamp, clear
  const ev = process.env.EV ? {} : { 2: 'Sound.blip(1)', 2.3: 'Sound.blip(2)', 2.6: 'Sound.blip(3)', 2.9: 'Sound.blip(4)', 3.2: 'Sound.blip(5)', 3.4: 'Sound.lock()', 4: 'Sound.send(false)', 5: 'Sound.beacon(false)',
    5.5: 'Sound.cell(.1)', 5.6: 'Sound.cell(.25)', 5.7: 'Sound.cell(.4)', 5.8: 'Sound.cell(.55)', 7: 'Sound.tlStep(0,1,true)', 7.2: 'Sound.tlStep(0,2,true)', 7.4: 'Sound.tlStep(0,3,true)', 7.7: 'Sound.tlRoll(true)', 8.2: 'Sound.tlStep(2,5,true)', 8.6: 'Sound.tlStep(4,6,true)', 9.2: 'Sound.tlTotal(true)',
    10.5: 'Sound.part()', 11: 'Sound.lampPay(0)', 11.3: 'Sound.lampPay(1)', 11.6: 'Sound.lampPay(2)', 12.5: 'Sound.beacon(true)', 13.5: 'Sound.full()', 15: 'Sound.clear()', 17: 'Sound.pick()', 17.5: 'Sound.warn()', 18: 'Sound.iceCash(3)', 19: 'Sound.stamp(2)' };
  if (process.env.NOFX) for (const k in ev) delete ev[k];
  if (process.env.EV) { const j = JSON.parse(process.env.EV); for (const k in j) ev[Number(k)] = j[k]; }
  const keys = Object.keys(ev).map(Number).sort((x, y) => x - y); let ki = 0;
  for (let t = 0; t <= DUR; t = Math.round((t + 0.05) * 100) / 100) { await pg.evaluate(`window.__vt = ${t}`);
    while (ki < keys.length && keys[ki] <= t) { await pg.evaluate(`__lex(${JSON.stringify(ev[keys[ki]])})`); ki++; }
    await pg.waitForTimeout(70); }
  const wav = await pg.evaluate(`(async () => { const buf = await window.__off.startRendering(), sr = buf.sampleRate, n = Math.floor(${DUR} * sr), ch = [buf.getChannelData(0), buf.getChannelData(1)];
   const out = new DataView(new ArrayBuffer(44 + n * 4)), w = (o, s) => { for (let i = 0; i < s.length; i++) out.setUint8(o + i, s.charCodeAt(i)); };
   w(0, 'RIFF'); out.setUint32(4, 36 + n * 4, true); w(8, 'WAVEfmt '); out.setUint32(16, 16, true); out.setUint16(20, 1, true); out.setUint16(22, 2, true); out.setUint32(24, sr, true); out.setUint32(28, sr * 4, true); out.setUint16(32, 4, true); out.setUint16(34, 16, true); w(36, 'data'); out.setUint32(40, n * 4, true);
   for (let i = 0; i < n; i++) for (let c = 0; c < 2; c++) { const v = Math.max(-1, Math.min(1, ch[c][i] || 0)); out.setInt16(44 + i * 4 + c * 2, v * 32767, true); }
   let s = ''; const u = new Uint8Array(out.buffer); for (let i = 0; i < u.length; i += 32768) s += String.fromCharCode.apply(null, u.subarray(i, i + 32768)); return btoa(s); })()`);
  console.log('station', await pg.evaluate(`__lex('Sound.station()')`));
  fs.writeFileSync(out, Buffer.from(wav, 'base64')); console.log('errors', errs); await b.close(); })();
