---
name: lexicon-signal-dev
description: Work on Lexicon Signal (repo lexicon-signal), Chris's late-night radio word game: change it, make and fit its painted art, test it on every screen, publish the phone link. Not for Hereafter Man or Port Stacker.
---

# Lexicon Signal dev loop (repo: lexicon-signal)

Chris's radio word game (Idle Looping Studios). One HTML page, played from the artifact link on his phone, in a browser with keys or
a controller, and later on his Retroid Pocket 2S and Pocket 6. This is the workflow as it runs today: when how something gets done
changes, update this skill (propose it again as an improvement) and the repo copy (`.claude/skills/lexicon-signal-dev/SKILL.md`) in
the same batch.

## Rules that always apply
- Originality (the repo is public): never name another game, game company, game character or a copyrighted/living artist anywhere in
  the repo: code, comments, docs, file names, commit messages, issues, art prompts saved here. Describe what something does instead.
  Talking about references with Chris in chat is fine; none of it goes in the repo.
- Before every commit run `python3 -I tools/namecheck.py` and read its list; remove anything that names something that isn't ours.
  The check holds no list of forbidden names on purpose.
- Never change Hereafter Man (christopherlunardi/Hereafter-Man-Claude-1) or Port Stacker Deluxe (christopherlunardi/port-stacker).
  Port Stacker may be cloned read-only for reference (the handheld shell came from its game/src/shell.html).
- Never type his passwords, never use OneDrive.

## Where things live
- `index.html`: the whole game, written as a page body (no doctype/html/head/body: the artifact host adds them). Sections in order:
  shell CSS (the studio's handheld: cream body on touch screens, d-pad, A/B, Select/Start pills; `padmode` when a controller is used,
  `inapp` for the future launcher), stage CSS, vibe overlays, markup, then one script.
- `words.js`: `window.LEX_WORDS`, the ENABLE list (public domain), 3-12 letters, space separated.
- `art/`: painted layers `room.png`, `window.png` (glass cut out), `view.png` (city, no tower), `tower.png` (pre-placed in view
  coordinates), `radio.png` (radio + side table, keyed out). `art/compose.py` layers and grades them into `art/scene.jpg` (1672x941),
  the only image the game loads. `art/tools/keyout.py` removes a magenta background.
- Live link: https://claude.ai/artifact/TcdvDWboTHP3Lh1RrqggS3 . Publish `index.html` with files
  `{"words.js": "words.js", "art/scene.jpg": "art/scene.jpg"}` (same file path keeps the URL).

## How the game is built
- Stage: a 1672x941 div showing scene.jpg; every live piece sits at painting coordinates (stage px). A camera (`layout()`) scales it to
  cover the screen; narrower screens crop to SPAN (335..1600: tower + radio), narrower still centre on the glass. Overlays (title, shop,
  game over) are placed over the visible part and scaled to stay readable (`compact` hides extra rows on small screens).
- Painting coordinates (from art/radio.png placed at x+230): tuning dial 895..1237 x 122..216; meter centre 1333,173 r58; glass panel
  895..1355 x 257..597 (grid 4x4 tiles 100x74, gap 9, origin 911,265); battery lamps x 995/1045/1095/1146/1196/1246, y 662, r18;
  knobs 890,660 and 1350,660 r45; window shade 218..528 x 130..265 (score); tower beacon 463,326; table apron y ~858 (part plaques).
  If the art changes, re-measure with a gridded close-up and update these numbers here and in the code.
- Rules of play: 4x4 grid, trace touching letters (8 directions), 3+ letters, word score = signal (letter values) x boost (length-2)
  x part multipliers; 5 words a night (lamps), 1 retune; night targets 40 x 1.42^(n-1) rounded to 5; pick 1 of 3 parts after each
  night. Letter weights and values are our own tables in the script.
- Planned (Chris 2026-11-12): used letters don't get replaced in place. The letters above them fall down their column with a heavy,
  mechanical drop (bounce + thud), and new letters slide in from the top to fill each column.
- Input: controller/keys first (A add letter, A on the last letter sends, B back, Start/Y retune, Select/X cycles the vibe), touch and
  mouse drag or tap on the glass. Gamepad standard mapping, bottom face = A.
- Effects: letters fly on a curve into the beacon, beacon flash + rings, score counts up on the shade, needle on the meter, sparks and
  dust motes on the fx canvas, static snow in the glass as the battery drains. Vibes: night (default), broadcast, film, clean.
- Sound: Web Audio synth only (84 BPM night pulse that opens up as the signal rises, plus effects). Starts on the first button press.

## Every change
1. Edit `index.html` (or art layers + `python3 -I art/compose.py`).
2. Syntax check: extract the inline script and `node --check` it.
3. Screenshots: wrap the page in a doctype/head into a scratch folder with words.js and art/scene.jpg, then shoot with Playwright
   (Chrome at /usr/bin/google-chrome) at desktop 1280x800 and phone 390x844 with touch on (portrait 4:3 crop), plus 640x480 for the
   Retroid 2S. Google Fonts are blocked in the sandbox, so fallback fonts show there; that's expected.
4. Name check (`tools/namecheck.py`), commit with a plain message, push, republish the link.
5. Tell Chris in a few lines what changed.

## Art: ChatGPT paints, we fit it
- Style: mid-century American realist oil painting, flat planes, strong geometric light, deep midnight blues and teals with warm amber
  lamp light, one red accent (the tower). Never name the painter in prompts saved to the repo.
- Make each piece as its own layer, and ask for a solid flat magenta (#FF00FF) background (ChatGPT's "transparent" often comes back as
  a painted checkerboard). Leave every moving part blank in the art (dial, meter face, lamps): the game draws those.
- Give Chris the WHOLE prompt every time, never "change this line". He attaches the scene so far as the style reference.
- Fitting: save uploads into art/, key out magenta with `art/tools/keyout.py`, cut rectangles in code when that's cleaner (the window
  panes), add the layer to `art/compose.py`, rebuild scene.jpg, check a composite before using it.
- Look: one warm grade over everything (compose.py), with a little more on the radio so it sits in the room's light. Live grain,
  vignette and the vibe overlays go on top in the page. Chris wants it warm, unified, and not corny.
- Open direction (2026-11-12): Chris wants to try mixing in a late-90s computer RPG feel (low-res sharp pixels, a shared 256-colour
  palette, palette-cycling glows, a chunky bevelled bottom HUD bar with a message log and a rolling counter), without fake CRT effects.
  Mock it as a still first.

## Working with Chris
- He dictates by voice; "I don't know" is a filler, not doubt.
- He sends quick notes while you work: fold them into the current batch, don't publish a half-done batch.
- Keep replies short and plain: what changed, then one question if one is needed. Show options as pictures when it's about looks.
- He only wants the Fable model (subagents) when he asks for it.
