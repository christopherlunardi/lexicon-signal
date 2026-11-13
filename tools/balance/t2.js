const { run, PARTS } = require("./sim.js");
const bot = process.argv[2] === "expert" ? { kind: "expert" } : { kind: "player", z: 3.0, eye: 1 }, RUNS = +process.argv[3] || 300;
const avg = (a) => a.reduce((x, y) => x + y, 0) / a.length;
function test(parts) { const R = []; for (let i = 0; i < RUNS; i++) R.push(run(bot, { parts, noShop: true, maxNight: 14 }));
  return { n: avg(R.map(r => r.nights)), pw: avg(R.flatMap(r => r.pts)), over: avg(R.map(r => r.over)) }; }
const base = test([]); console.log("base", base.n.toFixed(2), base.pw.toFixed(1));
const out = [];
for (const p of [...PARTS, "gold"]) { const row = [p]; for (const k of [1, 2, 3]) { if (p === "gold" && k > 1) { row.push("", ""); continue; } const r = test(Array(k).fill(p)); row.push((r.n - base.n).toFixed(2), (r.pw / base.pw).toFixed(2)); } out.push(row); console.log(row.join("\t")); }
