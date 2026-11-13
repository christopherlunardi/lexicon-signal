# Lexicon Signal (repo: lexicon-signal)

Chris's late-night radio word game (Idle Looping Studios). Trace words in a 4x4 letter grid inside an old radio's glass, beam them to
the radio tower outside the window, and fill each night's signal target before the battery lamps go dark. Clear a night, fit a radio
part; every run builds a different radio. One HTML page, played:
- from the artifact link on his phone (on-screen d-pad, A/B, Select/Start in the studio's handheld shell),
- in a browser with keys, mouse or any controller (controller and keyboard come first; touch and mouse also work),
- later on his Retroid Pocket 2S (640x480) and Pocket 6 (1920x1080) through a launcher app.

Read the workflow in `.claude/skills/lexicon-signal-dev/SKILL.md` before changing anything, and keep it up to date.

## Originality rules (the repo is public)
- Everything here is our own: names, art, words, sounds, music, code. Never copy another game's art, layouts, sounds, characters or names.
- Never name another game, game company or game character anywhere in this repo: code, comments, docs, art prompts kept here, file names,
  commit messages, issues or store text. Describe what a thing does instead of what it is "like".
- Don't name living or copyrighted artists either; describe the style (e.g. "mid-century American realist oil painting").
- Before every commit, run the name check in the skill and fix anything it finds. Keep the git history clean of those names too.

## Other projects
- Never change Hereafter Man (christopherlunardi/Hereafter-Man-Claude-1) or Port Stacker Deluxe (christopherlunardi/port-stacker) while
  working on this game. Port Stacker may be read for reference (its handheld shell is reused here), never written.

## Layout
- `index.html` the whole game (shell, canvas, script). Written as a page body: the artifact host adds the doctype and head.
- `words.js` the word list (ENABLE, public domain), 3-12 letters.
- `art/pixel/` the pixel art: sources in `src/`, `build.py` makes the palette, sprites, icons, fonts and `atlas.png`/`atlas.json`.
- `web/` the installable web app for GitHub Pages, made by `tools/web.py` (with `tools/web/pwa.js` and `sw.js`); never edit web/ by hand.
- `android/` the Retroid app (downloads the newest dist/lexicon-signal.html itself); `tools/release.py` makes dist/.
- `art/concept/look-target.png` the look we're matching. Older painted layers in `art/` are kept for reference only.
