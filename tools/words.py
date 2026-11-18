"""Builds words.js, the game's word list, from the lists in tools/wordlists/ (all searched as one):
  enable.txt    ENABLE (public domain), the original list
  scowl-70.txt  SCOWL / ESDB size 70 (American, British and Canadian spellings, no abbreviations), for modern everyday words;
                its copyright notice is tools/wordlists/SCOWL-Copyright.txt and must stay with it
  places.txt    place names (cities, states, countries) from the same ESDB data, size 60 and below (Chris 2026-11-14)
  names.txt     nationalities, languages, holidays, religions, planets and star signs (no first or last names)
  The list is written in five groups, most common first (SCOWL sizes from scowl-sizes.txt), split by " | ".
  extra.txt     our own words (optional): newer slang, internet and crude words the lists don't have, words separated by spaces or lines, # comments
Only plain a-z words of 3 to 12 letters are kept. usage: python3 -I tools/words.py"""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]; D = ROOT / "tools/wordlists"
words, counts, everyday = set(), {}, set()
for name in ["enable.txt", "scowl-70.txt", "places.txt", "names.txt", "extra.txt"]:
    f = D / name
    if not f.exists(): continue
    got = {w for l in f.read_text().splitlines() for w in l.split("#")[0].lower().split() if re.fullmatch(r"[a-z]{3,12}", w)}
    counts[name] = len(got - words); words |= got
    if name != "enable.txt": everyday |= got
# how common each word is (Chris 2026-11-18: the gold key should pick REPO, not PEPO): five groups, most common first, split by " | ":
# SCOWL size 35, 40-50, 60 (scowl-sizes.txt), then the rest of the everyday lists, then the words only ENABLE has
size = {l.split()[0]: int(l.split()[1]) for l in (D / "scowl-sizes.txt").read_text().splitlines() if l and not l.startswith("#")}
def tier(w):
    z = size.get(w)
    if z is not None: return 0 if z <= 35 else 1 if z <= 50 else 2
    return 3 if w in everyday else 4
groups = [set() for _ in range(5)]
for w in words: groups[tier(w)].add(w)
(ROOT / "words.js").write_text("// Word list: ENABLE (public domain) + SCOWL/ESDB size 70 (Copyright Kevin Atkinson, see tools/wordlists/SCOWL-Copyright.txt)"
    " + place names (ESDB, and the world-cities list from GeoNames, CC BY 4.0) + our own extra words; 3-12 letters. Made by tools/words.py\nwindow.LEX_WORDS=\"" + " | ".join(" ".join(sorted(g)) for g in groups) + "\";\n")
print(len(words), "words;", ", ".join(f"{k}: +{v}" for k, v in counts.items()))
