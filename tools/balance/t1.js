const { run, targetFor } = require("./sim.js");
const bots = { expert: { kind: "expert" }, player: { kind: "player", z: 3.0, eye: 1 }, casual: { kind: "player", z: 3.5, eye: .7 } };
const t0 = Date.now();
for (const [nm, bot] of Object.entries(bots)) { const R = []; for (let i = 0; i < 200; i++) R.push(run(bot, { noShop: true, maxNight: 12 }));
  const nights = R.map(r => r.nights), avg = (a) => a.reduce((x, y) => x + y, 0) / a.length;
  const reach = [1,2,3,4,5,6,7,8].map(n => (R.filter(r => r.nights >= n).length / R.length * 100).toFixed(0) + "%");
  const pts = R.flatMap(r => r.pts), wl = R.flatMap(r => r.words);
  console.log(nm.padEnd(7), "nights avg", avg(nights).toFixed(2), "clear n1..8", reach.join(" "), "| pts/word", avg(pts).toFixed(1), "len", avg(wl).toFixed(2)); }
console.log("targets", [1,2,3,4,5,6,7,8,9,10].map(targetFor).join(" "), (Date.now() - t0) + "ms");
