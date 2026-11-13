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
- **D-pad / gamepad:** move the cursor, A adds a letter (press it on the last letter to send), X sends the word, B steps back, Y retunes, Start pauses (sound, new run, quit to title; in the app also check for update, update the app and exit).
- **Keyboard:** WASD or arrows move, Space or Enter picks the letter (again on the last letter sends), Backspace takes one back, R retunes, Esc or P pauses, M sound.
- **Touch / mouse:** tap letters or drag across them; tap the right tuning knob to retune, the left one to pause; the phone's on-screen handheld has the d-pad, A, B, X and Y, and Select / Pause.

## Files

- `index.html` — the whole game (markup, styles, script).
- `words.js` — the word list (ENABLE, public domain), 3–12 letters.
- `art/` — the painted layers and `compose.py`, which builds `scene.jpg`.
- `CLAUDE.md` and `.claude/skills/lexicon-signal-dev/` — project rules and the dev workflow.

## Installable web app (phone and Retroid)

`python3 -I tools/web.py` (after `tools/release.py`) writes `web/`: the game as a self-contained offline site with a manifest, a
service worker and icons. GitHub Pages serves it (`.github/workflows/pages.yml`) at https://christopherlunardi.github.io/lexicon-signal/ .
Open that in Chrome and choose Install app (or Add to home screen): it runs full screen with no on-screen controller, in Chrome's own
engine, and plays offline. A new build downloads in the background and takes over on the next title screen.
