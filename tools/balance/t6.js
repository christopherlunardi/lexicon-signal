const { run, targetFor } = require("./sim.js");
const R = []; for (let i = 0; i < 300; i++) R.push(run({ kind: "player", z: 3.0, eye: 1 }, { maxNight: 12 }));
console.log("night target lampBonus | avg word / target | median | words/night");
for (let n = 1; n <= 9; n++) { const a = R.flatMap(r => r.byNight[n] || []).sort((x, y) => x - y); if (!a.length) continue;
  const runs = R.filter(r => r.byNight[n]).length;
  console.log(n, targetFor(n), Math.max(5, Math.round(targetFor(n) / 4 / 5) * 5), "|", (a.reduce((x, y) => x + y, 0) / a.length).toFixed(2), (a[a.length >> 1]).toFixed(2), "|", (a.length / runs).toFixed(1)); }
