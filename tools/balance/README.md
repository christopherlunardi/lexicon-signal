# Balance simulator

`sim.js` is the game's rules (scoring, parts, the glass, the shop, the leftover bonus) copied from index.html, with bots that play
them. It needs `dict.txt` (the word list, one per line) and `zipf.txt` (word frequencies, made with the `wordfreq` Python package)
next to it; neither is kept in git, make them with the snippet below. Keep the rules in sim.js in step with index.html.

    python3 -c "import re;from wordfreq import zipf_frequency as z;s=re.search(r'LEX_WORDS=\"([^\"]*)\"',open('words.js').read()).group(1).split(' ');open('tools/balance/dict.txt','w').write('\n'.join(s));open('tools/balance/zipf.txt','w').write('\n'.join(f'{w} {z(w,\"en\"):.1f}' for w in s if z(w,'en')>=2.5))"

Bots: `expert` knows every word and always sends the best; `player` knows common words (zipf >= 3) and spots each with a chance
that falls with length, then sends the best it spotted. Both retune when nothing on the glass gets near what each word needs.
- `t1.js` no parts: how far each bot gets. `t2.js <bot> <runs>` each part at 1, 2, 3 copies (nights gained, points per word).
- `t3.js` whole runs with the shop (random picks and ranked picks). `V=coil,echo,owl,short node t4.js ...` tries rule changes.
