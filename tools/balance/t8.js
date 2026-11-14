const { run } = require("./sim.js");
const avg = (a) => a.reduce((x, y) => x + y, 0) / a.length, bot = { kind: "player", z: 3.0, eye: 1 };
const test = (pp, N = 300) => { const R = []; for (let i = 0; i < N; i++) R.push(run(bot, { parts: pp, noShop: true, maxNight: 14 })); return R; };
const base = test([]), b = avg(base.map(r => r.nights));
for (const p of ["gold", "tap", "coil", "carrier"]) { const R = test([p]); console.log(p.padEnd(8), "nights +" + (avg(R.map(r => r.nights)) - b).toFixed(2), "| run score x" + (avg(R.map(r => r.total)) / avg(base.map(r => r.total))).toFixed(2)); }
