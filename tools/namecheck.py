"""Lists proper-noun-looking words in the repo (and in recent commit messages) that aren't ordinary dictionary words,
so a person can check that no other game, company, character or artist is named anywhere.
Usage: python3 -I tools/namecheck.py
No list of forbidden names is kept here on purpose: naming them would break the rule. Read the output and fix anything that names
something that isn't ours."""
import re, subprocess, sys

words = set(open("words.js").read().split('"')[1].split())
OURS = {  # our own names and ordinary technical terms that the dictionary lacks
    "lexicon", "signal", "idle", "looping", "studios", "chris", "claude", "retroid", "pocket", "android", "github",
    "enable", "html", "css", "svg", "json", "js", "py", "png", "jpg", "api", "dpad", "fm", "am", "bpm", "ui", "fx",
    "shortwave", "longwave", "javascript", "chrome", "safari", "google", "fonts", "bungee", "limelight", "space", "mono",
    "webkit", "moz", "rgba", "srgb", "gamepad", "playwright", "numpy", "pil", "chatgpt", "anthropic", "readme", "md",
    "opus", "co", "authored", "noreply", "hereafter", "ghost", "jail", "port", "stacker", "deluxe",
}
files = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split()
texts = {f: open(f, encoding="utf-8", errors="ignore").read() for f in files
         if f != "words.js" and not f.endswith((".png", ".jpg", ".jpeg", ".gif", ".mp3", ".mp4"))}
texts["(commit messages)"] = subprocess.run(["git", "log", "--format=%B"], capture_output=True, text=True).stdout
hits = {}
for name, t in texts.items():
    for w in re.findall(r"\b[A-Z][a-zA-Z]{2,}\b", t):
        lw = w.lower()
        if lw in words or lw in OURS or lw.rstrip("s") in words:
            continue
        hits.setdefault(w, set()).add(name)
if not hits:
    print("No unfamiliar proper nouns found.")
    sys.exit(0)
print("Check these (not dictionary words). Anything naming another game, company, character or artist must go:")
for w in sorted(hits):
    print(f"  {w:20s} {', '.join(sorted(hits[w]))[:90]}")
