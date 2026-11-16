// human-like bot runs, calibrated on Chris's play logs (2026-11-16). env: N runs, Z, RARE, GREEDY, RT, S3..S6 (spot chances), PICK=his|smart|random
const { run } = require("./sim.js");
const avg = (a) => a.reduce((x, y) => x + y, 0) / (a.length || 1);
const bot = { kind: "human", z: +(process.env.Z || 3), rare: +(process.env.RARE || .2), greedy: +(process.env.GREEDY || .6), rt: +(process.env.RT || 0),
  spot: { 3: +(process.env.S3 || .5), 4: +(process.env.S4 || .45), 5: +(process.env.S5 || .1), 6: +(process.env.S6 || .03), 7: +(process.env.S7 || .005) } };   // (tuned 2026-11-16: matches his word lengths, word commonness and lamps left per night)
// his picks, from the logs: red key stuff, gold, battery and the clock first; the amp, coil and knob almost never
const HIS = { red: 9, gold: 8, tap: 7, blue: 5, battery: 5, owl: 4, hat: 4, meter: 3, echo: 2, vowel: 2, treble: 1, short: 1, amp: .6, coil: .6, knob: .6 };
const RANK = ["red","coil","knob","gold","tap","blue","meter","amp","treble","owl","vowel","echo","battery","short","hat"];
const pick = process.env.PICK === "smart" ? (ch) => ch.slice().sort((a, b) => RANK.indexOf(a) - RANK.indexOf(b))[0]
  : process.env.PICK === "random" ? (ch) => ch[(Math.random() * ch.length) | 0]
  : (ch) => { const w = ch.map(p => HIS[p] || 1), t = w.reduce((a, b) => a + b); let r = Math.random() * t; for (let i = 0; i < ch.length; i++) if ((r -= w[i]) <= 0) return ch[i]; return ch[0]; };
const N = +(process.env.N || 200), R = [];
for (let i = 0; i < N; i++) R.push(run(bot, { pick, parts: process.env.START ? process.env.START.split(",") : [], maxNight: 25, trade: !!process.env.TRADE }));   // (no trades in the game since 2026-11-16)
const W = R.flatMap(r => r.words), Z = R.flatMap(r => r.wz || []);
const ld = {}; W.forEach(l => ld[Math.min(l, 7)] = (ld[Math.min(l, 7)] || 0) + 1);
const out = { nights: +avg(R.map(r => r.nights)).toFixed(2), median: R.map(r => r.nights).sort((a, b) => a - b)[N >> 1],
  len: Object.fromEntries(Object.entries(ld).map(([k, v]) => [k, +(v / W.length).toFixed(3)])), zipf: +avg(Z).toFixed(2), rareShare: +(Z.filter(z => z < 2.5).length / Z.length).toFixed(3),
  retunesPerRun: +avg(R.map(r => r.retunes)).toFixed(2), trades: +avg(R.map(r => r.trades || 0)).toFixed(2), melts: +avg(R.map(r => r.melts || 0)).toFixed(2), reqs: +avg(R.map(r => r.reqs || 0)).toFixed(2), overPerRun: +avg(R.map(r => r.over)).toFixed(2), score: Math.round(avg(R.map(r => r.total))) };
const NR = R.flatMap(r => r.nightRatio || []), byN = {}; NR.forEach(([n, x, wl]) => (byN[n] = byN[n] || []).push([x, wl]));
out.night = Object.fromEntries(Object.keys(byN).slice(0, 12).map(n => [n, { reach: +(R.filter(r => r.nights >= +n).length / N).toFixed(2), ratio: +avg(byN[n].map(v => v[0])).toFixed(2), left: +avg(byN[n].map(v => v[1])).toFixed(1) }]));
const wpn = R.flatMap(r => Object.values(r.wpn || {})); out.wordsPerNight = +avg(wpn).toFixed(2);
console.log(JSON.stringify(out));
