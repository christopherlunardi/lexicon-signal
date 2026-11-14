const { run } = require("./sim.js");
const avg = (a) => a.reduce((x, y) => x + y, 0) / a.length;
for (const [nm, bot] of [["casual", { kind: "player", z: 3.5, eye: .7 }], ["player", { kind: "player", z: 3.0, eye: 1 }]]) {
  const R = []; for (let i = 0; i < 200; i++) R.push(run(bot, { maxNight: 14 }));
  console.log((process.env.OLDLAMP ? "old " : "best") , nm, "nights", avg(R.map(r => r.nights)).toFixed(2), "run score", Math.round(avg(R.map(r => r.total))), "leftover share", (avg(R.map(r => r.bonus / Math.max(1, r.total))) * 100).toFixed(0) + "%"); }
