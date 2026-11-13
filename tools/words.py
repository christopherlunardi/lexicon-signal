"""Builds words.js, the game's word list, from the lists in tools/wordlists/ (all searched as one):
  enable.txt    ENABLE (public domain), the original list
  scowl-70.txt  SCOWL / ESDB size 70 (American, British and Canadian spellings, no abbreviations), for modern everyday words;
                its copyright notice is tools/wordlists/SCOWL-Copyright.txt and must stay with it
  extra.txt     our own words (optional): newer slang, internet and crude words the lists don't have, words separated by spaces or lines, # comments
Only plain a-z words of 3 to 12 letters are kept. usage: python3 -I tools/words.py"""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]; D = ROOT / "tools/wordlists"
words, counts = set(), {}
for name in ["enable.txt", "scowl-70.txt", "extra.txt"]:
    f = D / name
    if not f.exists(): continue
    got = {w for l in f.read_text().splitlines() for w in l.split("#")[0].lower().split() if re.fullmatch(r"[a-z]{3,12}", w)}
    counts[name] = len(got - words); words |= got
(ROOT / "words.js").write_text("// Word list: ENABLE (public domain) + SCOWL/ESDB size 70 (Copyright Kevin Atkinson, see tools/wordlists/SCOWL-Copyright.txt)"
    " + our own extra words; 3-12 letters. Made by tools/words.py\nwindow.LEX_WORDS=\"" + " ".join(sorted(words)) + "\";\n")
print(len(words), "words;", ", ".join(f"{k}: +{v}" for k, v in counts.items()))
