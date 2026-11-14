// whole runs with the shop under a target curve (T=base,earlyGrowth,lateGrowth): % of runs that clear each night
const { run, targetFor } = require("./sim.js");
const avg = (a) => a.reduce((x, y) => x + y, 0) / (a.length || 1), RUNS = +process.argv[2] || 150;
console.log("T=" + (process.env.T || "40,1.8,1.5"), "targets", [1,2,3,4,5,6,7,8,10,12].map(targetFor).join(" "));
for (const [nm, bot] of [["casual", { kind: "player", z: 3.5, eye: .7 }], ["player", { kind: "player", z: 3.0, eye: 1 }], ["expert", { kind: "expert" }]]) {
  const R = []; for (let i = 0; i < (nm === "expert" ? RUNS / 3 : RUNS); i++) R.push(run(bot, { maxNight: 20 }));
  console.log(" ", nm.padEnd(7), "avg last night", avg(R.map(r => r.nights)).toFixed(1), "| cleared:", [1,2,3,4,5,6,7,8,10,12].map(n => n + ":" + Math.round(R.filter(r => r.nights >= n).length / R.length * 100)).join(" ")); }
