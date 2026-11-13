const { run, PARTS, targetFor } = require("./sim.js");
const avg = (a) => a.reduce((x, y) => x + y, 0) / (a.length || 1);
const RANK = ["coil","heat","carrier","knob","gold","amp","treble","owl","vowel","echo","battery","short"];
const smart = (ch) => ch.slice().sort((a, b) => RANK.indexOf(a) - RANK.indexOf(b))[0];
for (const [nm, bot] of [["player", { kind: "player", z: 3.0, eye: 1 }], ["casual", { kind: "player", z: 3.5, eye: .7 }], ["expert", { kind: "expert" }]])
 for (const [pn, pick] of [["random", null], ["smart", smart]]) {
  const R = []; const RUNS = nm === "expert" ? 80 : 200; for (let i = 0; i < RUNS; i++) R.push(run(bot, { pick: pick || undefined, maxNight: 20 }));
  const reach = [3,4,5,6,7,8,9,10,12].map(n => n + ":" + (R.filter(r => r.nights >= n).length / R.length * 100).toFixed(0)).join(" ");
  const bonusShare = avg(R.map(r => r.bonus / Math.max(1, r.total)));
  console.log(nm.padEnd(7), pn.padEnd(6), "nights", avg(R.map(r => r.nights)).toFixed(2), "| cleared % by night", reach, "| over/run", avg(R.map(r => r.over)).toFixed(1), "| leftover share of score", (bonusShare * 100).toFixed(0) + "%", "| words used/night", (avg(R.map(r => r.pts.length / Math.max(1, r.nights + 1)))).toFixed(1)); }
