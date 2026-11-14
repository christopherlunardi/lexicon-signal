// Lexicon Signal balance simulator: the game's rules (copied from index.html) with bots that play them.
const fs = require("fs");
const D = __dirname + "/";
const WORDS = fs.readFileSync(D + "dict.txt", "utf8").split("\n");
const ZIPF = new Map(fs.readFileSync(D + "zipf.txt", "utf8").split("\n").map(l => { const [w, f] = l.split(" "); return [w, +f]; }));
// trie
const ROOT = {}; for (const w of WORDS) { let n = ROOT; for (const c of w) n = n[c] || (n[c] = {}); n.$ = w; }

const WEIGHTS = { E:12, A:9, I:8, O:8, N:6, R:6, T:6, S:5, L:4, U:4, D:4, G:3, B:2, C:2, M:2, P:2, F:2, H:2, W:2, Y:2, V:1, K:1, J:1, X:1, Qu:1, Z:1 };
const VALUES = { "?":0, A:1,E:1,I:1,O:1,U:1,N:1,R:1,S:1,T:1,L:1, D:2,G:2,H:2, B:3,C:3,M:3,P:3,F:3,W:3,Y:3, K:4,V:4, J:6,X:6, Qu:7,Z:7 };
const VOWELS = new Set(["A","E","I","O","U"]);
const PARTS = ["amp","battery","knob","coil","short","echo","owl","treble","vowel","carrier","heat"]; const RARE = ["gold","tap"];
const N = 5, NN = 25, BASE_WORDS = 6, OVERDRIVE = 1.5, SLOTS = 5, MELT_N = 5;
const TG = (process.env.T || '40,1.8,1.5').split(',').map(Number);   // base, growth for the first nights, growth after night 5
const targetFor = (n) => { let t = TG[0]; for (let k = 2; k <= n; k++) t *= k <= 5 ? TG[1] : TG[2]; return Math.round(t / 5) * 5; };
const round5 = (v) => Math.max(5, Math.round(v / 5) * 5);
const WT = Object.entries(WEIGHTS), WTOT = WT.reduce((a, [, w]) => a + w, 0);
let rnd = Math.random; const V = Object.fromEntries((process.env.V || '').split(',').filter(Boolean).map(k => [k, 1]));
function pickLetter() { let r = rnd() * WTOT; for (const [k, w] of WT) if ((r -= w) <= 0) return k; return "E"; }
const tile = () => ({ ch: pickLetter(), hot: false, wild: false });

function mk(parts) { const S = { parts: parts.slice(), night: 1, total: 0, melt: 0, grid: [] }; return S; }
const has = (S, id) => S.parts.filter(p => p === id).length;
const maxWords = (S) => BASE_WORDS + has(S, "battery"), maxRetunes = (S) => 1 + has(S, "knob");
function ensureHot(S) { while (!S.grid.some(t => t.hot)) S.grid[(rnd() * NN) | 0].hot = true;
  if (has(S, "gold")) while (!S.grid.some(t => t.wild)) { const t = S.grid[(rnd() * NN) | 0]; t.wild = true; t.ch = "?"; } }
const vc = (S) => S.grid.filter(t => VOWELS.has(t.ch)).length;
function fillGrid(S) { S.grid = Array.from({ length: NN }, tile); let g = 0; while (vc(S) < 6 && g++ < 50) S.grid[(rnd() * NN) | 0].ch = "AEIOU"[(rnd() * 5) | 0]; ensureHot(S); }
function collapse(S, used) { const us = new Set(used), moved = new Set();
  for (let col = 0; col < N; col++) { const keep = []; for (let row = N - 1; row >= 0; row--) { const i = row * N + col; if (!us.has(i)) keep.push({ t: S.grid[i], from: row }); }
    for (let j = 0; j < N; j++) { const row = N - 1 - j, i = row * N + col;
      if (j < keep.length) { S.grid[i] = keep[j].t; if (keep[j].from !== row) moved.add(keep[j].t); } else { const t = tile(); S.grid[i] = t; moved.add(t); } } }
  let g = 0; while (vc(S) < 5 && g++ < 50) { const fr = S.grid.filter(t => moved.has(t) && !VOWELS.has(t.ch) && !t.wild); if (!fr.length) break; fr[(rnd() * fr.length) | 0].ch = "AEIOU"[(rnd() * 5) | 0]; }
  ensureHot(S); }
const ADJ = Array.from({ length: NN }, (_, a) => { const r = []; for (let b = 0; b < NN; b++) if (a !== b && Math.abs(a % N - b % N) <= 1 && Math.abs(((a / N) | 0) - ((b / N) | 0)) <= 1) r.push(b); return r; });
// every word on the glass: {word, path}. Gold "?" takes any letter (the game uses the first letter, a..z, that makes a word).
function findAll(S) { const out = new Map(), path = [], seen = new Uint8Array(NN);
  function go(i, node) { const t = S.grid[i]; const chs = t.ch === "?" ? "abcdefghijklmnopqrstuvwxyz" : t.ch.toLowerCase();
    seen[i] = 1; path.push(i);
    if (t.ch === "?") { for (const c of chs) { const n = node[c]; if (n) step(n); } }
    else { let n = node; for (const c of chs) { n = n && n[c]; } if (n) step(n); }
    path.pop(); seen[i] = 0; }
  function step(n) { if (n.$ && n.$.length >= 3) { const k = n.$; if (!out.has(k) || out.get(k).length > path.length) out.set(k, path.slice()); }
    for (const j of ADJ[path[path.length - 1]]) if (!seen[j]) go(j, n); }
  for (let i = 0; i < NN; i++) go(i, ROOT);
  return [...out].map(([word, p]) => ({ word, path: p })); }
// one word's points, exactly as scoreOf in the game
function scoreOf(S, p, word) { const tiles = p.map(i => S.grid[i]), len = word.length, used = maxWords(S) - S.words, reds = tiles.filter(t => t.hot).length, h = (id) => has(S, id);
  let signal = 2 + tiles.reduce((s, t) => s + VALUES[t.ch], 0);
  signal += 3 * h("treble") * tiles.filter(t => VALUES[t.ch] >= 3).length + h("vowel") * tiles.filter(t => VOWELS.has(t.ch)).length;
  if (reds) signal += 5 * h("carrier");
  const boost = Math.max(1, len - 2) + h("amp") + (h("knob") ? S.retunes : 0); let mult = 1;
  if (h("coil") && len >= 5) mult *= 1.5 + h("coil") / 2;   // x2, x2.5, x3...
  if (h("short") && len <= 4) mult *= 1 + h("short");     // x2, x3...
  if (h("echo") && used === 0) mult *= 2 + h("echo");      // first word x3, x4...
  if (h("owl") && S.words === 1) mult *= 1 + 2 * h("owl"); // last word x3, x5, x7...
  if (reds) mult *= 2 + h("heat");
  const tap = has(S, "tap") && p.includes(12) ? (S.tap || 0) + len : 0;
  return Math.round(signal * boost * mult) + tap; }
function nightBonus(S) { const wl = Math.max(0, S.words), rl = Math.max(0, S.retunes), wv = process.env.OLDLAMP ? round5(S.target / 4) : S.nightBest, rv = round5(S.target / 6);
  return wl * wv + rl * rv + (wl && has(S, "owl") ? wv * (1 + 2 * has(S, "owl")) : 0); }

// bots. skill: "expert" knows every word and always sees the best; "player" knows common words (zipf >= z) and spots each one with
// a chance that falls with length, then sends the best of what it spotted.
const SPOT = { 3: .55, 4: .45, 5: .32, 6: .2, 7: .12 };
function candidates(S, bot) { let c = findAll(S);
  if (bot.kind === "player") c = c.filter(w => (ZIPF.get(w.word) || 0) >= bot.z && rnd() < (SPOT[Math.min(7, w.word.length)] * bot.eye));
  return c.map(w => ({ ...w, pts: scoreOf(S, w.path, w.word) })); }
function playNight(S, bot, st) {
  S.target = targetFor(S.night); S.score = 0; S.nightBest = 0; S.words = maxWords(S); S.retunes = maxRetunes(S); if (S.night === 1) fillGrid(S); else ensureHot(S);
  while (S.words > 0) {
    let c = candidates(S, bot); c.sort((a, b) => b.pts - a.pts); let best = c[0];
    const need = S.target - S.score, per = need / S.words;
    // retune when nothing on the glass gets close to what each word needs (a kept retune is worth a little with the knob)
    if (S.retunes > 0 && (!best || best.pts < per * .55)) { S.retunes--; fillGrid(S); st.retunes++; continue; }
    if (!best) { S.words = 0; break; }
    // a finisher: if a word clears the night, send the one that clears it (the biggest; overdrive helps)
    if (has(S, "tap") && best.path.includes(12)) S.tap = (S.tap || 0) + best.word.length; S.score += best.pts; S.total += best.pts; S.nightBest = Math.max(S.nightBest, best.pts); st.words.push(best.word.length); st.pts.push(best.pts); (st.byNight[S.night] = st.byNight[S.night] || []).push(best.pts / S.target);
    const used = best.path; S.words--; collapse(S, used);
    if (S.score >= S.target) { S.over = S.score >= S.target * OVERDRIVE; const b = nightBonus(S); S.total += b; st.bonus += b; return true; }
  }
  return false; }
function shop(S, pickFn) { const bag = PARTS.slice(), ch = []; while (ch.length < (S.over ? 4 : 3)) ch.push(bag.splice((rnd() * bag.length) | 0, 1)[0]);
  const rare = RARE.filter(r => !S.parts.includes(r)); if (rare.length && rnd() < (S.over ? .5 : 1 / 6)) ch[(rnd() * ch.length) | 0] = rare[(rnd() * rare.length) | 0];
  const kinds = new Set(S.parts), ok = ch.filter(p => kinds.has(p) || kinds.size < SLOTS);
  if (!ok.length) { S.melt++; if (S.melt >= MELT_N) { S.melt = 0; const st = [...kinds].filter(k => !RARE.includes(k)); if (st.length) S.parts.push(pickFn(st, S)); } return null; }
  const p = pickFn(ok, S); S.parts.push(p); return p; }
function run(bot, opts = {}) { const S = mk(opts.parts || []); const st = { nights: 0, words: [], pts: [], retunes: 0, bonus: 0, picks: [], over: 0, nightScores: [], byNight: {} };
  const pickFn = opts.pick || ((ch) => ch[(rnd() * ch.length) | 0]);
  while (S.night <= (opts.maxNight || 40)) { S.over = false; const ok = playNight(S, bot, st); st.nightScores.push(S.score / S.target);
    if (!ok) break; st.nights = S.night; if (S.over) st.over++;
    if (!opts.noShop) { const p = shop(S, pickFn); if (p) st.picks.push([S.night, p]); }
    S.night++; }
  st.total = S.total; st.parts = S.parts; return st; }
module.exports = { run, PARTS, targetFor, setRnd: (f) => rnd = f };
