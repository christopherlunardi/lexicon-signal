const { run } = require("./sim.js");
const bot = process.argv[2] === "expert" ? { kind: "expert" } : { kind: "player", z: 3.0, eye: 1 }, RUNS = +process.argv[3] || 300, parts = process.argv[4].split(",");
const avg = (a) => a.reduce((x, y) => x + y, 0) / a.length;
const test = (pp) => { const R = []; for (let i = 0; i < RUNS; i++) R.push(run(bot, { parts: pp, noShop: true, maxNight: 14 })); return avg(R.map(r => r.nights)); };
const b = test([]); console.log(process.env.V || "-", parts.map(p => p + " " + [1, 2, 3].map(k => (test(Array(k).fill(p)) - b).toFixed(2)).join("/")).join("  "));
