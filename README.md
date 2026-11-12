# Lexicon Signal

A late-night radio word game. Trace words through a grid of glowing letters, keep the signal alive, and build a different radio every run.

## How it plays

- A 4×4 grid of letters. Trace touching letters (any direction) to spell a word of 3+ letters.
- Each word scores **signal × boost**. Signal is the letter values added up, boost is the word length minus 2.
- You get 5 words a night (your battery). Reach the night's signal target before it runs out.
- Clear a night, then pick 1 of 3 radio parts. Parts change the letters you get or how words score.
- One retune per night rerolls the whole grid.

## Controls

- **Touch:** drag through letters and let go to send, or tap letters one by one and tap the last one again to send.
- **D-pad / gamepad:** move the cursor, A adds a letter (press it on the last letter to send), B steps back, Start or Y retunes, Select or X changes the look.
- **Keyboard:** type the word (letter keys), Enter sends, Backspace takes a letter back, Tab retunes, Esc turns sound on or off; arrows and Space also work.

## Files

- `index.html` — the whole game (markup, styles, script).
- `words.js` — the word list (ENABLE, public domain), 3–12 letters.
- `art/` — the painted layers and `compose.py`, which builds `scene.jpg`.
- `CLAUDE.md` and `.claude/skills/lexicon-signal-dev/` — project rules and the dev workflow.
