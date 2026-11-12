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
  Port Stacker may be cloned read-only for reference (the handheld shell and the Workshop page came from it).
- Never type his passwords, never use OneDrive.

## The look (decided 2026-11-12)
- Late-90s computer-game pixel art: a night room with damask wallpaper, a window with a city and a radio tower (red beacon), a big
  1940s wooden radio on a sideboard, and a wood-and-brass interface bar along the bottom (text log, two brass plates, part slots;
  the words-left gauge was dropped for more slots, the radio's six lamps show words left). The target picture is `art/concept/look-target.png`.
- Done the old-school way: the game draws at a real low resolution (W x 400, W = 532..950 from the screen's shape, 712 at 16:9; W x 425 with a 120-tall bar; screens narrower than 1.7:1, i.e. phones, get
  W x 495 with a 190-tall two-row bar; the room is 305 tall either way) and
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
  behind the radio's left edge (beacon still visible).
- Part slots (2026-11-12): always 5, on every screen (a rule of play, PART_SLOTS). Copies of one part stack in its slot (x2, x3).
  Wide screens: log | plates | 5 slots in one row. Narrow: log and plates on top, the 5 slots centred in a row under them.
  All 5 full and a new kind of part picked: the swap screen (phase "swap") asks which part to take out (all its copies go);
  left/right + A, or tap the slot; B or a tap on the room goes back to the picker. Picker cards say "STACKS: XN" or
  "SLOTS FULL: SWAP ONE". `#test-swap` opens the swap screen.
- The night's goal is a signal tube along the top of the bar, the full inner width (2026-11-12, Chris wanted a satisfying fill bar):
  a brass-capped glass channel (drawn in buildBar) with a row of light cells drawn on the fine layer (`drawTube`, `tubeGlows`).
  When a word reaches the tower, a glowing beam arcs from the beacon down to the tube's head and lands with a thump and sparks; only
  then does the count run. Each cell pops on white and fades to its colour (deep amber to gold to white-hot along the tube) with a
  click that climbs in pitch; a sheen runs along the lit part; a word that can be sent blinks the cells it would add; a full tube
  flashes, bursts and pulses white-hot, then the night clears. A new night drains it. `#test-word-fill` starts at 17 of 30.
- Slots show what their part is doing (2026-11-12, Chris: parts need a logical visual). Spare Battery and Fine Tuning Knob carry a
  lamp per copy in their slot: a battery lamp is an extra word (spent before the radio's six lamps), a knob lamp an extra retune
  (spent after the radio's own one); the log says when one is spent. A part that changes the traced word lights its slot frame;
  parts waiting for their moment (Echo Tube first word, Night Owl last word, Carrier) glow softly; Echo dims once used. When a word
  lands, every part that changed it flashes and a tag ("x2", "+6") rises off its slot (`partHits`, `slotState`, `drawSlotStates`).
  `#test-word-parts` fits two batteries, a knob, an echo tube and an amp.
- The room is built the full screen height (the sideboard's drawer rows carry on down, fading into shadow). On the title screen the
  bar is away; it rises into place with a thud when a run starts (`barShow` moves `L.barY`).
- Lit lamps are drawn on the fine layer (`drawLamp`) at the socket's true middle (`L.lamps`: half a pixel right of the marked
  point, the fifth one more), radius 7 world px, so they sit dead centre (2026-11-12, Chris saw them off-centre).
- The window (2026-11-12): Chris picked design 7 of 9 (stained glass sun across the top, tall pane below), 141 wide x 233 tall.
  Its ChatGPT source had no recoverable pixel grid (fix_pixel_art standard found nonsense, neural redrew it), so it was shrunk with
  our own k-centroid downscale (`art/pixel/kdown.py`): each pixel takes the main colour of what it covers, sharp and true. Use
  that when fix_pixel_art can't find the grid. build.py marks the panes (WIN_PANES, the glass: emissive, rain falls there), the
  light spots (window_lights: lit building windows, the stained glass; the game blooms them) and keeps the beacon's pink halo by
  keying only magenta that touches the picture's edge.
  The night is option 2's teal-green (Chris): build.py recolours the panes' blue pixels by brightness rank to option 2's colours,
  sampled from windows9.png; the rain is tinted to match.
- Rain (drawRain): faint slanted streaks and drops sliding down the panes in fits and starts, clipped to the panes and kept off
  the radio on narrow screens. The room's sound is rain (a soft filtered-noise wash, fine hiss, the odd drip); there is no constant
  static hiss any more (static is only a sound effect, e.g. retune).
- Bar contents always sit inside the bar's inner gold border, centred on one line with one equal gap.
- Part icons (2026-11-12, Chris found the old ones not good enough): build.py cuts each icon as the biggest blob in its sheet cell
  (no neighbour bits or specks). Slots draw the full icon on the fine layer at one art pixel per fine pixel (full detail, no shrink),
  lit softly from behind; never make the slots bigger (Chris). Stackable parts show a lamp per copy instead of an "x2".
  The part picker is three display cases 9-sliced from the slot frame, the icon at world size lit from behind, the name stamped on a
  brass plate (plate3, two lines on a taller plate if needed), the effect in lit amber, and a lamp label (NEW / STACKS X2 / SWAP A
  PART). The chosen case rises with a warm frame; the others dim. Score tags are small dark chips with dot-matrix figures.
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
  `{"words.js": "words.js", "studio.js": "studio.js", "art/pixel/atlas.png": "art/pixel/atlas.png", "art/pixel/atlas.json":
  "art/pixel/atlas.json"}`.

## Start of the game
- Splash ("PRESS ANY BUTTON"/"TAP TO START": a phone needs one press before it plays sound) -> the Idle Looping Studios intro
  (`studio.js`, copied unchanged from port-stacker's generated game/src/js/09c-studio.js; its player is in index.html, `studioStart`...
  `studioEnd`, picture on the sound's clock, any press skips) -> the title. Only our own hashes (#test-, #keys-, #title-) skip to the title; any other hash (the host can add one) still gets the splash and intro.
  Publish studio.js with the game.

## Title tips and sound
- The title dial scrolls game tips, one at a time in random order (`TIPS` in index.html). Keep them true: every change to a rule,
  number, control or part updates the tips it touches in the same batch; drop tips that no longer hold, add tips for new things.
- The title glass letters flicker at random, each on its own clock (`glassFl`): a random stutter to switch on, then frequent short
  random dips and the odd slow fade-out-and-back.
- Sound on phones: `Sound.ensure` sets the page's audio session to playback and loops a second of silence in an audio element, so
  an iPhone's silent switch doesn't mute the game (same fix as the studio's other games); finger-up, click and key presses also
  wake the sound.

## Dot glass keys (the play area)
- Letters flicker randomly and subtly: each key has its own random clock and now and then dips gently for a few frames; the whole
  letter dims at once: never single dots dropping out (Chris dislikes it; low-battery dot failure and per-dot shimmer were removed). Picked letters stay steady while the traced letters aren't a word yet; once they are, they flicker too, and a
  light wipe sweeps corner to corner across the word's keys one after another (`dotOkAt`), then a faint one runs through now and
  then while the word stays good (Chris, 2026-11-12: subtle, and the wipe only for a real word).

## Rules of play
- 4x4 keys in the radio glass; trace touching letters (8 directions), 3+ letters. Score = signal (letter values) x boost (length-2)
  x part multipliers; every word carries +2 signal so short words count. 6 words a night (one per lamp), 1 retune; targets
  30 x 1.4^(n-1) rounded to 5 (30, 40, 60, 80...); pick 1 of 3 parts. Night 1 was too hard at 40 in 5 words (Chris kept losing).
- The goal is said plainly: a night card over the glass at the start ("NIGHT 1 / BEAM 30 SIGNAL / IN 6 WORDS", any input dismisses
  it), the top plate shows "N TO GO" with a fill bar, the log says what's left after each word, and the tower beacon burns brighter
  as the night's signal fills.
- Used keys vanish; the keys above fall down their column with a heavy drop, one short bounce and a thud; new keys fall in from
  the top. No input while keys are falling or letters are flying.
- Sent letters fly to the tower beacon; it flashes and the score counts up on the plate; the log reports everything.
- The dial always shows the traced word's value on its right, counting up as letters go in (plain amber while it can't be sent).
  When it can be sent the whole dial lights warm, the word and number go bright and the number gets a "+". A hovered key (mouse,
  or the button cursor) previews dimly: its letter after the word and "+gain" before the number. Every key shows its value as dots.
- Input: buttons first (A add letter, A on the last letter sends, B back, Start/Y retune, Select/X/Tab/M sound on or off),
  touch/mouse drag or tap. Gamepad standard mapping, bottom face = A.
- Play area workshop (2026-11-12). Round 1 (six key styles: pixel keys, typewriter, glow tubes, neon glass, ivory tiles, brass keys;
  KEY_STYLES 0..5): Chris picked glow tubes (index 2) but wanted the play area to have more vibe. Round 2 adds
  five whole play-area directions, KEY_STYLES 6..10: valve bank, signal scope, stencil plates, switchboard, dot glass. They draw the
  whole glass on the fine layer (`drawPlayArea`, one `pa...` function each, plus `paGlows` and `paFlyers`) and share a few clocks:
  `t.lit` (traced, eased), `t.land` (just landed), `lockK` (word can be sent), `addT`/`sendT`/`arriveT`, and `ghosts` (the places a
  sent word left). In these looks letters lift off before they fly and the keys above wait a little longer before falling.
  The game is one game with one look: dot glass (KS 10, a const) on every link and in every browser (Chris: no versions) (2026-11-12: a style remembered in one browser made Chris's phone
  and Claude window look different); `#keys-N` no longer switches looks (`#test-word-keys-N` with a word traced). Web fonts:
  Special Elite, Bungee Hairline, Bungee, Limelight, Share Tech Mono, Stardos Stencil, Alfa Slab One. Value dots stay in every style
  (Chris likes them), bright enough to read on unselected keys. He likes it dark with smooth glow. Select is the sound switch again.

## Every change
1. Art: save the upload to `art/pixel/src/`, run it through fix_pixel_art (save as NAME_fixed.png), add its entry in `build.py`
   (crop and marked points in source pixels), run `python3 -I art/pixel/build.py`, check a still with `mock.py`.
   Code: edit `index.html`.
2. Syntax check: extract the inline script and `node --check` it.
3. Screenshots: copy index.html (wrapped in doctype/head), words.js and art/pixel/atlas.* into a scratch folder, serve it with
   `python3 -m http.server` (fetch needs http), shoot with Playwright (Chrome at /usr/bin/google-chrome) at 1280x800, phone
   390x844 with touch, and 640x480. Add `#test-shop` (part picker) or `#test-word` (RAT traced) to the URL for set-up screens.
   The web fonts are blocked in the sandbox: install @fontsource packages with npm and add local @font-face rules to the test page.
   Clips: a hash ending in `-step` (e.g. `#test-word-keys-6-step`) stops the game running by itself; `LEXSTEP(n)` advances n
   frames. Press keys with Playwright, step 2 frames, screenshot the canvas, repeat, then encode with ffmpeg (30 fps, H.264,
   yuv420p, no sound) into `workshop/img/<topic>-<round>/`. A Workshop option's images may be .mp4 files.
4. Name check, commit with a plain message, push, republish the link. Tell Chris in a few lines what changed.

## Workshop (options Chris looks at and plays, like the other games)
- Lexicon Signal Workshop: https://claude.ai/artifact/LuTEWxDDeCazkUDjiXCrdj , built from `workshop/` (index.html + workshop.json +
  img/<topic>-<round>/). `python3 -I workshop/build.py` makes the playable copy `workshop/play.html` (+ words.js, art/pixel/atlas.*,
  generated, not in git); an option's `play` is `play.html#...` (the game reads `#keys-N`, `#test-word`, `#test-shop` from the hash).
- When Chris asks for options for anything, they go on the Workshop as a new topic or round.
- A round in workshop.json: question, found, status open|decided (+chosen), options {id, title, note, images [{src,label}], play}.
- Publish index.html with `root` workshop and a files map of everything new (unchanged files are kept). Capabilities: db rule
  feedback read/write owner, plus user; omit them on republish.
- Read his answers: ArtifactData list on the Workshop, collection `feedback`, doc `<topic>-<round>` {pick, notes{id:text}, general,
  submitted}. Act on submitted ones, then mark the round decided (chosen) in workshop.json and republish.
- title-r1 (open, 2026-11-12): five title entrances in the game, TITLE_STYLES 1..5 (tuning in, from the tower, neon across the street,
  fill the tube, programme sheet, 6 radio close-up (Chris's sketch: no bar, radio at 3 fine px per art px, title lit as keys in the
  glass, PRESS START plate). The glass is Chris's painted picture (`art/title/`: build.py splits glass-title-src.jpg into
  glass-lit/glass-dim + a box per letter; the game fades each letter's box of the lit one over the dim one: switch-on stutter,
  breathing, the odd dropout). Publish art/title/glass-lit.png, glass-dim.png, glass.json with the game.; 0 = the old parchment box). The game opens on 6 now (Chris: put it in while we tweak it), `#title-N` opens one (`#title-N-step` for clips).
  The logo is a placeholder built in code (`buildLogo`/`drawLogo`: LEXICON in bevelled brass cells, SIGNAL in lit dot-matrix,
  waves); a real logo from ChatGPT replaces it later. A press during an entrance skips to its settled screen (`titleBusy`).
- Rounds: keys-r1 decided (glow tubes), keys-r2 decided: first signal scope, then Chris saw dot glass on his phone and switched to it (KS 10, always on).
  Next: build dot glass out as THE play area and drop the other styles' code.

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
