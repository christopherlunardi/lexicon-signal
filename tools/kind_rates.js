// How often an ordinary player sends each kind of word (the personality types' "base"), from real play data (Chris 2026-11-24: the
// numbers should come from real players, but the game stays fully offline: they are baked into index.html and refreshed by hand
// from time to time, until they settle and get frozen).
//
// 1. Export every player's sent words from the play database (Neon project lexicon-plays, table plays) with this SQL, and save the
//    rows as JSON {pid: "word word ..."} (owner runs included; each player counts once):
//      SELECT pid, string_agg(lower(w->>'w'), ' ') AS words FROM plays, jsonb_array_elements(data->'words') w GROUP BY pid
// 2. With the local server on :8771 (python3 -m http.server 8771 in the repo): node tools/kind_rates.js words.json
//    It sorts each word into kinds with the game's own kindsOf(), takes each player's share of each kind, averages the players
//    (each counts the same, so one heavy player doesn't define "ordinary"), blends that with the first guesses while there are few
//    players (weight K: with K players, half real, half guess), writes tools/kind_rates.json and puts the numbers into PTYPES.
// 3. Release as usual. When the numbers stop moving between refreshes, set FROZEN in kind_rates.json and stop refreshing.
const { chromium } = require("playwright"); const fs = require("fs"); const path = require("path");
const ROOT = path.resolve(__dirname, ".."), K = 4, MIN_WORDS = 50;
const GUESS = { edgelord: .012, online: .007, tileshark: .07, wordcel: .02, doomer: .009, short: .22, long: .08, romantic: .005, gourmand: .015 };
(async () => {
  const P = JSON.parse(fs.readFileSync(process.argv[2], "utf8")), b = await chromium.launch(), p = await b.newPage();
  await p.goto("http://localhost:8771/index.html#test-book-title"); await p.waitForTimeout(2500);
  const shares = JSON.parse(await p.evaluate((P) => __lex(`JSON.stringify(Object.fromEntries(Object.entries(${JSON.stringify(P)}).map(([id, s]) => { const ws = s.split(" ").filter(Boolean), c = {}; ws.forEach(w => kindsOf(w).forEach(k => c[k] = (c[k] || 0) + 1)); return [id, { n: ws.length, c }]; })))`), P));
  await b.close();
  const players = Object.entries(shares).filter(([, v]) => v.n >= MIN_WORDS), n = players.length, rates = {}, real = {};
  for (const k in GUESS) { real[k] = players.reduce((a, [, v]) => a + (v.c[k] || 0) / v.n, 0) / Math.max(1, n); rates[k] = +((GUESS[k] * K + real[k] * n) / (K + n)).toFixed(4); }
  const out = { date: new Date().toISOString().slice(0, 10), players: n, words: players.reduce((a, [, v]) => a + v.n, 0), K, guess: GUESS, real, rates, FROZEN: false };
  fs.writeFileSync(path.join(ROOT, "tools/kind_rates.json"), JSON.stringify(out, null, 1) + "\n");
  const f = path.join(ROOT, "index.html"); let s = fs.readFileSync(f, "utf8");
  for (const k in rates) { const re = new RegExp(`(\\n  ${k}: \\{[^\\n]*?base: )[0-9.]+`); if (!re.test(s)) throw new Error("no PTYPES line for " + k); s = s.replace(re, `$1${String(rates[k]).replace(/^0\./, ".")}`); }
  fs.writeFileSync(f, s);
  console.log(`${n} players, ${out.words} words`); for (const k in rates) console.log(k.padEnd(10), "guess", (GUESS[k] * 100).toFixed(1) + "%", " real", (real[k] * 100).toFixed(1) + "%", " now", (rates[k] * 100).toFixed(2) + "%");
})();
