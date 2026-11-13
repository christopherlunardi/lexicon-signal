---
name: lexicon-signal-dev
description: Work on Lexicon Signal (repo lexicon-signal), Chris's late-night radio word game: change it, make and fit its pixel art, test it on every screen, publish the phone link. Not for Hereafter Man or Port Stacker.
---

# Lexicon Signal dev loop (repo: lexicon-signal)

Chris's radio word game (Idle Looping Studios). One HTML page, played from the artifact link on his phone, in a browser with keys or
a controller, and as an installed offline web app (GitHub Pages) on his Retroid Pocket 2S and phones. This is the workflow as it runs today: when how something gets done
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
  keying only magenta that touches the picture's edge. A sash bar (a copy of the transom) crosses the tall pane at SASH_Y so it
  reads as a window that opens; the panes split there (rain stays off the bar).
  The night is option 2's teal-green (Chris): build.py recolours the panes' blue pixels by brightness rank to option 2's colours,
  sampled from windows9.png; the rain is tinted to match.
- Rain (drawRain): faint slanted streaks and drops sliding down the panes in fits and starts, clipped to the panes and kept off
  the radio on narrow screens. The room's sound is rain (a soft filtered-noise wash, fine hiss, the odd drip); there is no constant
  static hiss any more (static is only a sound effect, e.g. retune).
- Every part's effect shows where it acts (Chris 2026-11-12: "no visual indicator that I have another word"). A Spare Battery adds
  a small light on the radio's bottom lip under the lamp row (one per battery, centred), separate from the tuning lights; spare
  words are spent first. A used lamp or light flares white and fades with a click. Retunes are small lamps on the base lip under the right (tuning) knob, one per retune a night, lit while
  unused (a Fine Tuning Knob adds one). Slot lamps still show copies too. Any new part gets a visual like this in the same batch.
- The radio's round meter (top right) was painted out in build.py (a mirror of the cabinet's plain left side, plus plain wood
  beside it); the spot is free for something better later. drawMeter is unused.
- Never put a // comment in the middle of a line of code: it silently cuts off the calls after it (it hid the whole play area once).
- The radio is radio5 (482 x 274 true size, glass 229 x 152): ChatGPT redraw of the old radio with a bigger glass, fixed with
  fix_pixel_art (standard) and its rows evened out (SQUARE 3.236). The old 4x4 radio source stays in src/ for reference. The title's
  painted glass is still the 4x4 picture, kept in proportion inside the bigger glass for now.
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
- `words.js`: `window.LEX_WORDS`, made by `python3 -I tools/words.py` from `tools/wordlists/` (2026-11-13): ENABLE (public domain),
  SCOWL/ESDB size 70 (American, British, Canadian spellings, no abbreviations; free, keep `SCOWL-Copyright.txt` with it; built from
  github.com/en-wl/wordlist with `./scowl word-list 70 A,B,Z,C 1 --deaccent --wo-poses=abbr`) and our own `extra.txt` (newer slang,
  internet and crude words with their forms; crude words are allowed (Chris), slurs against groups and brand names are not). 3-12 letters.
  Add words to extra.txt and rerun; never edit words.js by hand. Chris wants to talk about a bigger list of our own later.
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
- The game's look (Chris 2026-11-12, Workshop glass-r1): dot glass with three of the round's takes together, set by GF in the script:
  deep glass (recessed key wells, each letter's soft glow on the dots round it, a faint curved reflection on the pane), clear path
  (lit links from key edge to key edge with arrowheads and a running bead, a lit stud on the first key, nothing crosses a letter)
  and lift-off (sent letters rise whole off the glass while the fill drains down the key, then break into dots with a few sparks;
  the send holds a little longer). `#glass-N` still opens a single take (#glass-0 is plain dot glass from before).
- The traced word's path (Chris: its order wasn't clear): a lit line from key to key through their middles (soft glow + bright core,
  brighter once it's a real word), a ring on the first key, and three bright beads running along it from first letter to last.
- Letters flicker randomly and subtly: each key has its own random clock and now and then dips gently for a few frames; the whole
  letter dims at once: never single dots dropping out (Chris dislikes it; low-battery dot failure and per-dot shimmer were removed). Picked letters stay steady while the traced letters aren't a word yet; once they are, they flicker too, and a
  light wipe sweeps corner to corner across the word's keys one after another (`dotOkAt`), then a faint one runs through now and
  then while the word stays good (Chris, 2026-11-12: subtle, and the wipe only for a real word).

## Rules of play
- Parts and the red key (Chris 2026-11-13): EVERY part stacks (each copy adds the same again) and the picker can offer any part.
  A red key is always on the glass (a word through it x2; two red keys in a word x3). The parts: Tube Amp +1 boost; Spare Battery
  +1 word; Fine Tuning Knob +1 retune and +1 boost per retune still kept; Long Wave Coil 5+ letter words x(1+copies); Shortwave
  Crystal 3-4 letter words +6 signal; Echo Tube the first (copies) words x2; Night Owl Clock last word x(2+copies); Treble Slider +3
  signal per letter worth 3+; Vowel Antenna vowels +1 signal each (it no longer adds vowels: that made scores worse); Red Lamp (id
  carrier) +1 red key; Red Heat (id heat, the fuse icon via `icon`) red keys multiply one more. Static Filter was dropped.
  Every slot shows a lamp per copy. Score = signal (letter values + 2 + adds) x boost (length - 2, at least 1, + adds) x multipliers.
- Targets 30 x 1.5^(n-1) rounded to 5 (30, 45, 70, 100, 150...). Balance is checked with a bot simulator (three skill levels on the
  real word list, letter draw and parts; kept in the session scratchpad as bal/sim.js and partval.js): with this curve a casual bot
  runs ~7 nights, a good one ~11, a strong one ~16. Rerun it after any change to scoring, parts or targets.
- The red key (2026-11-13): always exactly one; a word through it x(2 + Red Heat copies). Red Lamp (id carrier, its red lamp icon)
  now adds +5 signal per copy to a word through the red key. Rare parts (`rare:true`, gold frame and gold label RARE: ONCE ONLY,
  offered one night in six, one in two after an overdrive, never twice): the Gold Key (id gold) puts a gold wildcard key "?" on
  the glass (t.wild, ch "?", value 0); resolveWord() reads it as the first letter that makes a real word. It can also be the red key
  (then it's any letter and doubles). Its icon is a stand-in drawn in build.py until src/gold_icon_fixed.png exists.
  Tests: #test-word-gold, #test-shop-gold.
- Play log (2026-11-13, Chris: study how people really play): every word (night, word, points, length, multiplier, red/gold used,
  words and retunes left, seconds taken), failed tries, retunes, parts offered and picked, nights and how the run ended. Kept on
  the device in localStorage lexsig.runs (last 40 runs); on the claude.ai link also saved to the artifact database, collection
  "plays" (owner reads; read it with ArtifactData list). The web app and Android app have no database: pause menu SHARE PLAY LOG
  sends the log through the phone's share sheet (or copies it). Use the logs to build human-like bots for the balance check.
- Part labels (Workshop tags-r1, Chris picked 3, the lit line): cardTag() draws a thin brass rule near the case's foot with the label
  lit under it (gold for rare). Layout rule: every case keeps a TAG_ZONE (64 fine px) at its foot that nothing else may enter, and
  all cases grow to the tallest one's needs (shopGeom); `#test-shop-all-N` shows parts 4N..4N+3 to check.
- Title menu (MENU_STYLE 6, Chris's art src/title_console.png cut to tpanel / tplate / tplate_lit): the wooden console under the
  radio with a brass plate per option (START, HOW TO PLAY, HIGH SCORES), the chosen one pressed in and lit; slice3Cv stretches a
  sprite from its ends and repeated middle.
- Melter art is in the atlas (iconL_melter, iconL_molten) for the planned melter: once all slots are full the picker offers MELT;
  five melts fill its lamps and give a wildcard upgrade (+1 copy of a fitted part). Not built yet.
- Arcade scoring (Chris 2026-11-13: the goal is a high score, the run goes on until you lose): the run score is all signal beamed
  (S.total), shown in the dial's marquee and at game over; the best ten runs on this device are kept in localStorage lexsig.scores
  (HIGH SCORES on the title menu, HIGH SCORE n under it, NEW HIGH SCORE / NUMBER n ON YOUR BOARD at game over).
- Overdrive: finish a night at OVERDRIVE (1.5) x its target or more: a red flash over the room, OVERDRIVE on the dial, and the part
  picker offers four instead of three. The tube's end lamp burns red while the traced word would do it. `#test-word-od` is 5 short.
  The picker's cases grow to fit the longest description; keep part descriptions short.
- Red Lamp checked (2026-11-13): stacking red keys grows only slowly (+12-16% a copy, five copies +55-71%); the Long Wave Coil and
  Tube Amp stacks are the strong ones (three coils +232% for a good player).
- The letters carry over from night to night (only a new run fills a fresh glass), so a big word can be saved for later.
- Reading a part (INSPECT): tap its slot, or press down past the bottom row and left/right along the slots; a card above the bar
  gives its name, what a copy does, how many are fitted and what it adds to the traced word. Up/A/B or a tap elsewhere closes it.
- 5x5 keys in the radio glass (N, NN in the script; 4x4 until 2026-11-12, when the radio was redrawn as radio5 with a glass about
  25% bigger so the keys stay the same size; H5() maps an old 4x4 position onto the 5x5 grid); trace touching letters (8 directions), 3+ letters. Score = signal (letter values) x boost (length-2)
  x part multipliers; every word carries +2 signal so short words count. 6 words a night (one per lamp), 1 retune; targets
  30 x 1.4^(n-1) rounded to 5 (30, 40, 60, 80...); pick 1 of 3 parts. Night 1 was too hard at 40 in 5 words (Chris kept losing).
- The goal is said plainly: a brass plaque that drops in at the top of the room with a clunk ("NIGHT 1 / BEAM 30 SIGNAL IN 6 WORDS"),
  holds, then lifts away (any press sends it off; Chris disliked the old dark box over the glass), the top plate shows "N TO GO" with a fill bar, the log says what's left after each word, and the tower beacon burns brighter
  as the night's signal fills.
- Used keys vanish; the keys above fall down their column with a heavy drop, one short bounce and a thud; new keys fall in from
  the top. No input while keys are falling or letters are flying.
- Sent letters fly to the tower beacon; it flashes and the score counts up on the plate; the log reports everything.
- The dial always shows the traced word's value on its right, counting up as letters go in (plain amber while it can't be sent).
  When it can be sent the whole dial lights warm, the word and number go bright and the number gets a "+". A hovered key (mouse,
  or the button cursor) previews dimly: its letter after the word and "+gain" before the number. Every key shows its value as dots.
- Input (Chris 2026-11-12: a four-button game, Start is a real pause, Select doesn't mute): A add letter, A on the last letter sends,
  X sends from anywhere, B back, Y retune (also R, or tapping the right tuning knob), Start pause (Esc/P). The phone shell has all
  four face buttons in a diamond (X SEND top, Y RETUNE left, A TUNE right, B BACK bottom; .btns --dia/--fb) and the SELECT and PAUSE
  pills. Select alone does nothing (held 1.5 s: dev panel). The pause menu (pauseItems) is RESUME, SOUND, NEW RUN,
  QUIT TO TITLE, and in the app CHECK FOR UPDATE / LOAD NEW BUILD, UPDATE APP (when launcher.json is newer) and EXIT GAME; anything
  that throws the run away asks twice. The Android launcher maps BUTTON_X to "x" and BUTTON_Y to "y".
  Colours on Android: the launcher uses a 32-bit window and turns off WebView dark recolouring (forceDark / algorithmic darkening,
  values-v29 forceDarkAllowed=false); the screen canvas is opaque ({alpha:false}).
- Render scale (2026-11-12, after Chris's side-by-side video of the Pocket 2S lagging behind his phone): everything draws in fine
  units (CVW x CVH = W*FINE x H*FINE; never use cv.width/cv.height for layout). When the screen shows the canvas at under .62 of its
  size in device pixels, RS = .5: the canvas holds half the pixels each way and draw() starts with ctx.setTransform(RS,...) (the title
  close-up's own setTransform multiplies by RS). ctx.imageSmoothingEnabled is forced on while RS < 1 so halved text never drops rows.
  The pause menu's foot shows FPS, draw ms, FULL/HALF size and the canvas size: ask Chris to read it off the device.
- Screen colour (pause menu, saved in lexsig.colour): NORMAL / SOFT / SOFTER, a CSS filter on the canvas (less saturation, a touch
  darker, hue nudged from red toward orange). The 2S screen shows the warm browns far redder and stronger than a phone; the page
  itself sends the same colours, so this is a per-screen setting, not a fix in the art.
- Fonts: Chris doesn't want outside display fonts on the game screen (2026-11-12: "big blocky text... doesn't match anything").
  The pause menu is a logbox parchment panel in the game's own "key" lettering; the start prompt is back to the dial's "dot"
  lettering. The smooth fonts (HOWF) stay only on the How to Play cards, which he liked.
- Tube end lamp (Chris 2026-11-12): a round lamp at the right end of the signal tube lights and pulses only while the traced word would
  fill the tube (S.score + pts >= S.target); a word that falls short never lights the last preview cell. How to Play's FILL THE TUBE
  card and the tips say so. Test with #test-word-near (score 3 short) and #test-word-fill.
- Sound on the handheld (Chris heard crackling): in the app the AudioContext uses latencyHint "playback" (bigger buffers), the music
  pads use one oscillator per note instead of a detuned pair, and a limiter (DynamicsCompressor) sits after master so stacked sounds
  can't clip. Keep idle sources off the sound thread: nothing runs into a silent gain.
  Also
  touch/mouse drag or tap. Gamepad standard mapping, bottom face = A.
- Keyboard (Chris 2026-11-12, after a typing experiment he rejected: the keyboard does NOT type words): WASD/arrows move, Space or
  Enter picks the letter under the cursor (again on the last letter sends), Backspace back, R retune, M sound. Keep keys few and
  clear, and list them in the line under the game.
- Mouse/touch: click or tap letters, or drag across them. A click on a key that doesn't touch the last letter keeps the word and
  flashes MUST TOUCH (it used to restart the word from that key, which looked like the word vanishing). With one letter picked, a
  click elsewhere just moves the start.
- Play area workshop (2026-11-12). Round 1 (six key styles: pixel keys, typewriter, glow tubes, neon glass, ivory tiles, brass keys;
  KEY_STYLES 0..5): Chris picked glow tubes (index 2) but wanted the play area to have more vibe. Round 2 adds
  five whole play-area directions, KEY_STYLES 6..10: valve bank, signal scope, stencil plates, switchboard, dot glass. They draw the
  whole glass on the fine layer (`drawPlayArea`, one `pa...` function each, plus `paGlows` and `paFlyers`) and share a few clocks:
  `t.lit` (traced, eased), `t.land` (just landed), `lockK` (word can be sent), `addT`/`sendT`/`arriveT`, and `ghosts` (the places a
  sent word left). In these looks letters lift off before they fly and the keys above wait a little longer before falling.
  The game is one game with one look: dot glass (KS 10, a const) on every link and in every browser (Chris: no versions) (2026-11-12: a style remembered in one browser made Chris's phone
  and Claude window look different); `#keys-N` no longer switches looks (`#test-word-keys-N` with a word traced). Web fonts:
  Special Elite, Bungee Hairline, Bungee, Limelight, Share Tech Mono, Stardos Stencil, Alfa Slab One. Value dots stay in every style
  (Chris likes them), bright enough to read on unselected keys. He likes it dark with smooth glow. (Select no longer switches sound: that's in the pause menu, or M.)

## Title menu and How to Play
- The title's brass plate is a menu: START and HOW TO PLAY, an arrow by the one you're on (up/down, A or Start; tap a line).
- HOW TO PLAY (`HOW_CARDS`): six cards over a live demo of the real game run by a small script (cursor moves, letters picked, words
  sent, retune, the part picker): spell a word, letters must touch, send it, fill the tube, retune, radio parts. The card pops up in a
  spot that doesn't matter for what's shown (HOW_AT: the wall left of the radio; below the tower light when the beam matters; on
  phones, the bar under the tube, or between the picker and slots for parts), and what it's about is ringed with a moving dashed
  glow (howTarget). NEVER shrink the game or cover what's being shown (Chris). Its words are smooth type at the page's real size (title Alfa Slab One, text Special Elite; Chris said the
  big pixel letters looked terrible and off-centre), button chips with centred labels. A/right next, B/left back (B on the first: title), tap right/left half. The demo never clears the night.
- ALWAYS keep How to Play true to the game (Chris): any change to a rule, number, control, part or what something looks like
  updates the card text and its demo script in the same batch, along with the dial TIPS.

## Dev mode (owner only, the same as the studio's other games)
- Ways in: on by itself from a file, a #dev link, unlocked before on this device (localStorage lexsig.devkey), or claude.ai says
  you own the artifact (window.claude.use("user").isOwner(); the game artifact declares the user capability); the secret combo on
  any pad, the handheld's buttons or keys: DOWN DOWN UP UP RIGHT LEFT RIGHT LEFT B A; or the dev code (same code and hash as the
  other games): press and hold the name above the screen about a second, or tap it five times.
- Once on: a DEV button in the name bar and ` open the panel (Esc closes); on a pad or the handheld, hold SELECT ~1.5 s (a short
  press does nothing); the d-pad moves, A presses, B/SELECT/START close. The panel: fit any part (works this
  night), take parts out, endless words, +1 word/retune, +10 signal, win/lose night, next/previous night, new letters, part
  picker, new run, title, studio intro, sound. Nothing is saved. New parts appear by themselves (it reads PARTS).

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
4. `python3 -I tools/release.py` then `python3 -I tools/web.py` (the Android build and the web app). Name check, commit with a plain
   message, push (that deploys the web app), republish the link. Tell Chris in a few lines what changed.

## The Retroid app (Android, built the same way as the studio's other game)
- Since 2026-11-12 the installable web app (below) is the main way to play on the Retroid; this app stays until Chris says otherwise.
- `android/`: a small launcher app (MainActivity, ApkProvider; package com.idlelooping.lexiconsignal, fixed sideload key
  lexiconsignal-sideload.jks). On start and on coming back it reads dist/version.json from GitHub (main); if that build is newer it
  downloads dist/lexicon-signal.html, checks its sha256 and replaces the older copy, then plays the newest build it has (the
  downloaded one or the one inside the app). Offline it plays what it has. It sends the buttons to the game's ssKey(name, down),
  calls ssInApp(), ssUpdateReady(build) (loads on the title screen) and ssAppUpdate(code) (UPDATE APP on the title menu).
- `.github/workflows/android.yml` builds the app on GitHub when android/ changes and puts it on the "launcher" release:
  https://github.com/christopherlunardi/lexicon-signal/releases/download/launcher/LexiconSignal.apk (Chris installs it once).
- Every game change that should reach the Retroids: `python3 -I tools/release.py` (bumps tools/build.txt, writes the one-file
  dist/lexicon-signal.html with words, studio intro, art and fonts inside, and dist/version.json), then commit and push.
  The page reads window.LEX_ASSETS when present (that build) and fetches the art files otherwise (the phone link).

## The installable web app: the main way to play on the Retroid and phones (2026-11-12)
- Live at https://christopherlunardi.github.io/lexicon-signal/ (GitHub Pages, source: GitHub Actions). Installed on Chris's Retroid
  Pocket 2S as a Chrome web app.
- Why: the Android app runs inside the 2S's built-in WebView, which is locked at v80 (firmware RP2S V1.0.0.37, Aug 2023, already
  the newest; it can't be updated). Measured there: ~15 fps (65 ms frames, GPU only 4 ms: WebView's own graphics thread was the
  bottleneck), audio crackle, and a slow intro (the intro runs on the sound clock, so a struggling sound thread drags it). Chrome 157
  on the same device runs the game fast. The web app runs in Chrome's current engine, so it is now the main way to play there.
- Keep the Android app (android/, dist/) building and working for now. Ask Chris before retiring it.
- Build: `python3 -I tools/web.py`, always after `tools/release.py` (every content change needs a new build number: the service
  worker's cache is named lexsig-BUILD and an unchanged number keeps serving the old files). It writes `web/`: index.html wrapped in
  a full head (manifest link, theme colour, icons, the fonts from web/fonts instead of the internet, window.LEX_BUILD, pwa.js at the
  end), words.js, studio.js, the art (atlas + title glass), icons (192, 512 and a maskable 512, made from the radio sprite with LS
  in dial dots), manifest.webmanifest, version.json, pwa.js and sw.js (their sources are tools/web/pwa.js and tools/web/sw.js), and
  .nojekyll. Never edit web/ by hand. Commit web/; `.github/workflows/pages.yml` deploys it on every push that changes web/.
- Manifest: name "Lexicon Signal", display fullscreen (display_override fullscreen then standalone), orientation landscape, dark
  background/theme (#0b0806), id/start_url/scope "./" (relative to the Pages path).
- pwa.js: when the page runs installed (display-mode fullscreen or standalone, or navigator.standalone) it adds body.pwa, which hides
  the controller, the name bar and the foot line and makes the screen fill the display (it needs align-self/justify-self stretch:
  the shell's grid rules otherwise shrink the fixed screen). Opened as a normal web page nothing changes. .pwa is not .inapp (that
  one changes the sound and expects the Android bridge). A controller works through the normal Gamepad API.
- Updates: sw.js precaches every file of the build and serves from the cache (offline it runs entirely from it; version.json always
  goes to the network). On launch with a network pwa.js asks for an update; a new build downloads in the background and waits.
  pwa.js then sets window.LEX_RELOAD and calls the game's ssUpdateReady(build): the game switches on the title screen (right away
  if it's there, otherwise on the next START; never mid-game; reloadBuild uses LEX_RELOAD when present, else the Android bridge),
  and the old cache is deleted.
- Touch has no Start button: tapping the radio's left knob pauses (the right one retunes). Everything else is reachable by touch.
- Installing on the Retroid: Daijisho (Chris's home launcher) hides Chrome's install option, so: Android settings > Home app >
  Quickstep, force-stop Chrome, reopen the site in Chrome, ⋮ > "Install and create shortcut" > Install, then set the Home app back
  to Daijisho. The device's settings are Chris's to change: tell him the steps, don't change them yourself.
  On a phone: open the link in Chrome, ⋮ > Install app (or Add to Home screen).
- Testing here: serve a folder holding a `lexicon-signal` link to web/ with http.server (the Pages path), check the manifest and
  service worker, go offline and reload, play a word (count oscillators made through an AudioContext wrapper for sound); fake
  installed mode by patching matchMedia in an init script (the display-mode emulation in the dev tools protocol doesn't take).
- Testing on the device (when the session has a shell on Chris's PC): the Retroid is on adb, at
  %LOCALAPPDATA%\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools\adb.exe.
  `adb shell dumpsys gfxinfo com.idlelooping.lexiconsignal` gives the Android app's frame times; SurfaceFlinger shows nothing for
  Chrome's surface, so read the web app's speed from the pause menu's FPS line instead. Esc or Back sent over adb closes the app.

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
- menu-r1 (open, 2026-11-12): five title-menu looks under the radio, MENU_STYLE 1..5 (bar and parchment, brass plates, station
  buttons, dial windows, parchment tags), `#menu-N`; each option its own container on dark floorboards (Chris: no bare black).
- glass-r1 (open, 2026-11-12; Chris compared dot glass with the old green scope look, kept dot glass and asked for variations of
  it): six takes on dot glass, GLASS_STYLE 1..6 (deep glass: recessed wells, letter bloom, curved sheen; warm-up: letters strike on
  as keys land; word lock: the word's keys flash and lock, the rest of the glass dips; clear path: edge-to-edge links with
  arrowheads; lift-off: sent letters rise off the glass while the fill drains; side meter: deeper amber, the value as a lamp stack
  beside the letter). 0 = the game's look, untouched and the default (`paDotGlass` hands over to `paGlassVar` only when
  GLASS_STYLE > 0; its pictures are cached in `gvSpr`). `#glass-N` opens one, `#test-word-glass-N` with RAT traced, `-step` on the
  end for clips. Media in workshop/img/glass-r1/ (glass-N.mp4, glass-N.jpg, glass-N-close.jpg; every clip is the same seeded
  sequence: take T back, add it again so the word locks, X to send, pick four letters, B four times). Whole-frame time at 640x480
  with the processor slowed 6x (Playwright, CDP Emulation.setCPUThrottlingRate, a 1-pixel read after each step so the drawing is
  really done): every option within noise of option 0 or a little faster. When Chris picks, fold the chosen ideas into
  paDotGlass and drop the rest.
- Speed (2026-11-12, Chris: the app lagged): the game steps at a fixed 60 a second (loop), glows are cached sprites (bloomSpr),
  resting keys draw from two cached layers (dotKeyCache), the dial's dot field is cached; keep per-frame drawing lean.
- carrier-r1 (decided: 5, red scan, now the game's look): five looks for the Carrier Lamp's red key in dot glass, HOT_STYLE 1..5 (red letter, red
  backlight, ember fill, pilot lamp, red scan), `#hot-N` opens one (`#test-word-hot-N` fits the carrier). No red outline (Chris).
  A picked red key fills red in every look.
- title-r1 (open, 2026-11-12): five title entrances in the game, TITLE_STYLES 1..5 (tuning in, from the tower, neon across the street,
  fill the tube, programme sheet, 6 radio close-up (Chris's sketch: no bar, radio at 3 fine px per art px, title lit as keys in the
  glass, PRESS START plate). The glass is Chris's painted picture (`art/title/`: build.py splits glass-title-src.jpg into
  glass-lit/glass-dim + a box per letter; the game fades each letter's box of the lit one over the dim one: switch-on stutter,
  breathing, the odd dropout). Publish art/title/glass-lit.png, glass-dim.png, glass.json with the game.; 0 = the old parchment box). The game opens on 6 now (Chris: put it in while we tweak it), `#title-N` opens one (`#title-N-step` for clips).
  The logo is a placeholder built in code (`buildLogo`/`drawLogo`: LEXICON in bevelled brass cells, SIGNAL in lit dot-matrix,
  waves); a real logo from ChatGPT replaces it later. A press during an entrance skips to its settled screen (`titleBusy`).
- tgap-r1 (decided: 1 blank keys, now the game's look, 2026-11-13): what fills the dark strips beside the painted 4x4 logo in the wider 5x5 title glass, TITLE_GAP 0..5
  (as now, blank keys, soft edges, thicker frame, band scales, zoom to fill), `#title-6-tgap-N`; drawn once into titleBg (titleGapDraw).
- goldkey-r1 (open, 2026-11-13): how the Gold Key looks and works on the glass, GOLD_STYLE 0..5 (0 as now and the default, letter reel,
  gold lamp board, shows its letter, brass housing, gilded word), `#goldkey-N`; `#test-word-gold-goldkey-N` fits it with the gold key
  at H5(13) and nothing traced (L, I, N then the gold key makes LINE), `#test-word-goldred-goldkey-N` makes it the red key too. All in
  `gkKey` / `gkBase` / `gkGlow` / `gkAfter` (cached in gvSpr); in 1..5 the key shows the letter it stands for (`gkLetterOf`) and that
  letter is sent in gold (flyer/ghost `gold`), the beacon flashes gold (`goldFlash`), 4 and 5 bring the beam and tube down gold too.
  Media in workshop/img/goldkey-r1/ (gold-N.mp4: gold key, then the same as the red key; gold-N.jpg; gold-N-close.jpg). Frame time at
  640x480, processor slowed 6x: every option within noise of option 0 (about 27-30 ms at rest, 28-35 with a word, both ways).
- Rounds: keys-r1 decided (glow tubes), keys-r2 decided: first signal scope, then Chris saw dot glass on his phone and switched to it (KS 10, always on).
  Next: build dot glass out as THE play area and drop the other styles' code.

## Art prompts (ChatGPT)
- The Vowel Antenna icon was redrawn on its own (src/vowel_icon.png, k-centroid shrunk to vowel_icon_fixed.png, 35x62) and swapped
  in after the palette is taken in build.py, so the interface colours don't shift. Do the same for any other single redrawn icon.
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
