const { run } = require("./sim.js");
const avg = (a) => a.reduce((x, y) => x + y, 0) / (a.length || 1);
const RANK = ["coil","heat","carrier","knob","gold","amp","treble","owl","vowel","echo","battery","short","hat"];
const smart = (ch) => ch.slice().sort((a, b) => RANK.indexOf(a) - RANK.indexOf(b))[0];
for (const [nm, bot] of [["player", { kind: "player", z: 3.0, eye: 1 }], ["casual", { kind: "player", z: 3.5, eye: .7 }]]) {
  const R = []; for (let i = 0; i < 120; i++) R.push(run(bot, { pick: smart, parts: process.env.START ? process.env.START.split(',') : [], maxNight: 20, trade: !!process.env.TRADE }));
  const reach = [5,6,7,8,9,10,12].map(n => n + ":" + (R.filter(r => r.nights >= n).length / R.length * 100).toFixed(0)).join(" ");
  console.log(process.env.TAG, nm, "nights", avg(R.map(r => r.nights)).toFixed(2), "|", reach, "| trades", avg(R.map(r => r.trades || 0)).toFixed(2), "| reqs/run", avg(R.map(r => r.reqs || 0)).toFixed(2), "| nights per req", avg(R.flatMap(r => r.reqWait || [])).toFixed(2), "| score", Math.round(avg(R.map(r => r.total || 0)))); }
