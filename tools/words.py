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
# within the most common group, how many everyday lists have the word (scowl-common.txt, Chris 2026-11-24): the gold key's tie-breaker,
# written after the five groups as two more lists (in 2 lists | in 0-1 lists), each a subset of group 0
lists = {l.split()[0]: int(l.split()[1]) for l in (D / "scowl-common.txt").read_text().splitlines() if l and not l.startswith("#")}
sub = [sorted(w for w in groups[0] if lists.get(w, 3) == 2), sorted(w for w in groups[0] if lists.get(w, 3) < 2)]
(ROOT / "words.js").write_text("// Word list: ENABLE (public domain) + SCOWL/ESDB size 70 (Copyright Kevin Atkinson, see tools/wordlists/SCOWL-Copyright.txt)"
    " + place names (ESDB, and the world-cities list from GeoNames, CC BY 4.0) + our own extra words; 3-12 letters. Made by tools/words.py\nwindow.LEX_WORDS=\"" + " | ".join(" ".join(sorted(g)) for g in groups) + "\";\nwindow.LEX_SUB0=\"" + " | ".join(" ".join(g) for g in sub) + "\";\n")
# word kinds for the Station Logbook's personality types (Chris 2026-11-23): kinds.txt's base words plus their plain forms (s, es, ed,
# ing) that are in the list; edgelord also takes extra.txt's "# crude" section. Written into words.js as window.LEX_KINDS.
kinds, cur = {}, None
for l in (D / "kinds.txt").read_text().splitlines():
    l = l.split("#")[0].strip().lower()
    if not l: continue
    if l.startswith("["): cur = kinds.setdefault(l.strip("[]"), set()); continue
    for w in l.split(): cur.update(f for f in [w] + [w + x for x in ("s", "es", "ed", "ing")] if f in words and (f == w or len(w) >= 3))
crude, on = set(), False
for l in (D / "extra.txt").read_text().splitlines():
    if l.startswith("#"): on = l.strip() == "# crude"; continue
    if on: crude.update(w for w in l.lower().split() if w in words)
kinds["edgelord"] |= crude
with open(ROOT / "words.js", "a") as f: f.write("window.LEX_KINDS={" + ",".join(f'{k}:"{" ".join(sorted(v))}"' for k, v in kinds.items()) + "};\n")
print("kinds:", ", ".join(f"{k} {len(v)}" for k, v in kinds.items()))
print(len(words), "words;", ", ".join(f"{k}: +{v}" for k, v in counts.items()))
