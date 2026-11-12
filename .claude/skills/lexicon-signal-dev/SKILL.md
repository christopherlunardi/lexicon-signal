---
name: lexicon-signal-dev
description: Work on Lexicon Signal (repo lexicon-signal), Chris's late-night radio word game: change it, make and fit its pixel art, test it on every screen, publish the phone link. Not for Hereafter Man or Port Stacker.
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

## The look (decided 2026-11-12)
- Late-90s computer-game pixel art: a night room with damask wallpaper, a window with a city and a radio tower (red beacon), a big
  1940s wooden radio on a sideboard, and a wood-and-brass interface bar along the bottom (text log, two brass plates, battery gauge,
  part slots). The target picture is `art/concept/look-target.png`.
- Done the old-school way: the game draws at a real low resolution (W x 400, W = 532..950 from the screen's shape, 712 at 16:9) and
  the canvas is scaled up with hard square pixels. Every art piece is shown at its TRUE pixel size, never resized (2026-11-12):
  ChatGPT's pixel art is fake pixels of uneven size, so each source is run once through RetroDiffusion's fix_pixel_art (standard
  engine, $0.002; pass the raw.githubusercontent.com URL of the source in the public repo; the result comes back as base64 in a saved
  tool-result file) and saved as `src/NAME_fixed.png`. If a fixed image comes back with non-square pixels (the UI kit did), its rows
  are evened out (SQUARE in build.py). Resizing art to fit a layout is what made it look rough: size the layout to the art instead.
  The room's light (lamp low right, moonlight round the window, darker edges) is applied smoothly per layout, no palette snapping,
  fairly dark (ambient ~.44; Chris found brighter too much). The window glass is emissive (skips room light). Live things are drawn
  with pixel lines; no CRT filter. Light is a smooth glow pass on the fine layer (`drawGlows`): beacon, the unseen lamp, battery
  lamps, dial, meter, lit keys, flying letters, sparks. Never dithered pixel halos (Chris doesn't like them).
- Things rearrange by screen shape: the wallpaper is a tile, the sideboard and bar are left end + repeated middle + right end, panels
  are 9-sliced from the log box, the bar is made taller by repeating its plain middle rows. Narrow (4:3) screens tuck the window
  behind the radio's left edge (beacon still visible) and show fewer part slots.
- Bar contents always sit inside the bar's inner gold border, centred on one line with one equal gap.
- Part icons: full size (iconL_) in the part picker, exactly half (icon_, 2x2 majority) in the bar's slots.
- Display rules: the screen canvas is twice the world size (FINE = 2). The room, keys, bar and menu panels draw in world pixels and
  are scaled up; every display draws on the fine grid on top: the dial is a lit amber dot-matrix (all dot positions faintly visible,
  marquee when idle), the meter needle and ticks are fine lines, the log types itself out in ink with a blinking cursor (older lines
  fade), plates are stamped (dark letters, light edge under), counts on slots are outlined. All lettering is our own 5x7 font (F5 in
  the script): ink = 5x7 at 2 fine px, dot = 5x7 dots, key = the same letters smoothed 2x and made bold. Selected keys light up
  amber with dark letters. On small screens (phones) text scales 1.5x (TK) and the log shows 2 lines.

## Where things live
- `index.html`: the whole game, written as a page body (the artifact host adds doctype/head). Shell CSS first (the studio's
  handheld: d-pad, A/B, Select/Start; `padmode` with a controller, `inapp` for the future launcher), then one canvas and one script.
- `words.js`: `window.LEX_WORDS`, the ENABLE list (public domain), 3-12 letters.
- `art/pixel/src/`: ChatGPT sources (wallpaper, window, radio, sideboard, uikit, icons) and their `_fixed` versions.
  `art/pixel/build.py` cuts every sprite from the fixed images at true size (crops and points written in source pixels), builds the
  wallpaper tile, the window glass mask, the 12 part icons at two sizes and the interface palette, and packs it all into
  `art/pixel/atlas.png` + `atlas.json` (the only art the game loads).
  `art/pixel/preview.py` / `mock.py` render stills of the room / full screen for judging. `art/pixel/pix.py` = palette helpers.
- The old painted version's layers and `art/compose.py` are kept in `art/` for reference; the game no longer uses them.
- Live link: https://claude.ai/artifact/TcdvDWboTHP3Lh1RrqggS3 . Publish `index.html` with files
  `{"words.js": "words.js", "art/pixel/atlas.png": "art/pixel/atlas.png", "art/pixel/atlas.json": "art/pixel/atlas.json"}`.

## Rules of play
- 4x4 keys in the radio glass; trace touching letters (8 directions), 3+ letters. Score = signal (letter values) x boost (length-2)
  x part multipliers. 5 words a night (lamps + battery gauge), 1 retune; targets 40 x 1.42^(n-1) rounded to 5; pick 1 of 3 parts.
- Used keys vanish; the keys above fall down their column with a heavy drop, one short bounce and a thud; new keys fall in from
  the top. No input while keys are falling or letters are flying.
- Sent letters fly to the tower beacon; it flashes and the score counts up on the plate; the log reports everything.
- The dial always shows the traced word's value on its right, counting up as letters go in (plain amber while it can't be sent).
  When it can be sent the whole dial lights warm, the word and number go bright and the number gets a "+". A hovered key (mouse,
  or the button cursor) previews dimly: its letter after the word and "+gain" before the number. Every key shows its value as dots.
- Input: buttons first (A add letter, A on the last letter sends, B back, Start/Y retune, Select/X/Tab key style, M sound),
  touch/mouse drag or tap. Gamepad standard mapping, bottom face = A.
- Key area workshop (open, 2026-11-12): six key styles live in the game (KEY_STYLES: pixel keys, typewriter, glow tubes, neon glass,
  ivory tiles, brass keys), Select cycles them, remembered per browser; `#test-word-keys-N` opens style N. Smooth styles draw on the
  fine layer with web fonts (Special Elite, Bungee Hairline, Bungee, Limelight). Value dots stay in every style (Chris likes them), bright enough to read on unselected keys.
  When he picks one, keep it, drop the rest, and give Select back to sound.

## Every change
1. Art: save the upload to `art/pixel/src/`, run it through fix_pixel_art (save as NAME_fixed.png), add its entry in `build.py`
   (crop and marked points in source pixels), run
   `python3 -I art/pixel/build.py`, check a still with `mock.py`. Code: edit `index.html`.
2. Syntax check: extract the inline script and `node --check` it.
3. Screenshots: copy index.html (wrapped in doctype/head), words.js and art/pixel/atlas.* into a scratch folder, serve it with
   `python3 -m http.server` (fetch needs http), shoot with Playwright (Chrome at /usr/bin/google-chrome) at 1280x800, phone
   390x844 with touch, and 640x480. Add `#test-shop` (part picker) or `#test-word` (RAT traced) to the URL for set-up screens.
4. Name check, commit with a plain message, push, republish the link. Tell Chris in a few lines what changed.

## Workshop (options Chris looks at and plays, like the other games)
- Lexicon Signal Workshop: https://claude.ai/artifact/LuTEWxDDeCazkUDjiXCrdj , built from `workshop/` (index.html + workshop.json +
  img/<topic>-<round>/). `python3 -I workshop/build.py` makes the playable copy `workshop/play.html` (+ words.js, art/pixel/atlas.*,
  generated, not in git); an option's `play` is `play.html#...` (the game reads `#keys-N`, `#test-word`, `#test-shop` from the hash).
- A round in workshop.json: question, found, status open|decided (+chosen), options {id, title, note, images [{src,label}], play}.
- Publish index.html with `root` workshop and a files map of everything new (unchanged files are kept). Capabilities on first publish:
  db rule feedback read/write owner, plus user; omit them on republish.
- Read his answers: ArtifactData list on the Workshop, collection `feedback`, doc `<topic>-<round>` {pick, notes{id:text}, general,
  submitted}. Act on submitted ones, then mark the round decided (chosen) in workshop.json and republish.
- Open rounds: keys-r1 (letter key look, 6 options).

## Art prompts (ChatGPT)
- One layer at a time, the look target attached for style. Pixel-art wording: low-resolution late-1990s computer game look, crisp
  hard-edged square pixels, no anti-aliasing, limited palette, small ordered dithering. Lit flatly and evenly (the game adds light).
- Solid flat pure magenta (#FF00FF) background, never "transparent" (it comes back as a painted checkerboard).
- Leave every live part blank (dial, meter, glass, lamps, slots, plates): the game draws those.
- Long pieces drawn evenly so the middle can repeat. UI kits: separate pieces with magenta space between.
- Give Chris the WHOLE prompt every time, never "change this line". To explore looks, ask for 6-9 options in one grid image.

## Working with Chris
- He dictates by voice; "I don't know" is a filler, not doubt.
- He sends quick notes while you work: fold them into the current batch, don't publish a half-done batch.
- Keep replies short and plain: what changed, then one question if one is needed. Show looks as pictures.
- He only wants the Fable model (subagents) when he asks for it.
