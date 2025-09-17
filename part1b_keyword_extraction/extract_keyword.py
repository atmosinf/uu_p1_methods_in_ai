import re
import unicodedata
from pathlib import Path
from typing import Dict, Optional, List

# ========= config =========
PRICERANGE_VALUES = {"cheap", "moderate", "expensive", "dontcare"}
AREA_VALUES       = {"north", "south", "east", "west", "centre", "dontcare"}
FOOD_VALUES       = {
    "italian","british","french","indian","chinese","japanese","thai","korean",
    "vietnamese","mediterranean","spanish","portuguese","greek","turkish",
    "american","mexican","european","bistro","gastropub","asian oriental","venetian",
    "dontcare"  # <-- added here
}

PRICERANGE_SYNONYMS = {
    "moderately": "moderate",
    "moderately priced": "moderate",
    "mid": "moderate", "midrange": "moderate", "mid-range": "moderate",
    "affordable": "moderate",
    "budget": "cheap", "low": "cheap", "inexpensive": "cheap",
    "pricey": "expensive", "high end": "expensive", "high-end": "expensive",
    "any": "dontcare", "any price": "dontcare",
    "dont care": "dontcare", "don't care": "dontcare",
    "doesnt matter": "dontcare", "doesn't matter": "dontcare",
}

AREA_SYNONYMS = {
    "center": "centre", "city center": "centre", "city centre": "centre", "downtown": "centre",
    "north part of town": "north", "south part of town": "south",
    "east part of town": "east", "west part of town": "west",
    "any": "dontcare", "anywhere": "dontcare",
    "dont care": "dontcare", "don't care": "dontcare",
    "doesnt matter": "dontcare", "doesn't matter": "dontcare",
}

FOOD_SYNONYMS = {
    "europe": "european", "britain": "british", "portugese": "portuguese",
    "gastro pub": "gastropub", "asian-oriental": "asian oriental", "asian/oriental": "asian oriental",
    "any": "dontcare", "any food": "dontcare",
    "dont care": "dontcare", "don't care": "dontcare",
    "doesnt matter": "dontcare", "doesn't matter": "dontcare",
}

# ========= helpers =========
def _norm(s: str) -> str:
    s = s.lower()
    # s = "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))
    s = re.sub(r"[^\w\s'&/-]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _compile_patterns(phrases):
    cleaned = sorted({_norm(p) for p in phrases if p}, key=len, reverse=True)
    patterns = [(p, re.compile(rf"(?i)\b{re.escape(p)}\b")) for p in phrases]
    return patterns

_PRICE_PATTERNS = _compile_patterns(PRICERANGE_VALUES | set(PRICERANGE_SYNONYMS.keys()))
_AREA_PATTERNS  = _compile_patterns(AREA_VALUES | set(AREA_SYNONYMS.keys()))
_FOOD_PATTERNS  = _compile_patterns(FOOD_VALUES | set(FOOD_SYNONYMS.keys()))

def _apply_syn(v: str, syn: Dict[str, str]) -> str:
    v = _norm(v)
    return syn.get(v, v)

def _canon(v: Optional[str], allowed, syn) -> Optional[str]:
    if not v:
        return None
    nv = _apply_syn(v, syn)
    return nv if nv in allowed else nv

def _first_hit(patterns, text: str) -> Optional[str]:
    for phrase, pat in patterns:
        if pat.search(text):
            return phrase
    return None

# ========= public API =========
def extract_keywords(text: str) -> Dict[str, Optional[str]]:
    t = _norm(text)
    out = {"pricerange": None, "area": None, "food": None}

    p = _first_hit(_PRICE_PATTERNS, t)
    a = _first_hit(_AREA_PATTERNS, t)
    f = _first_hit(_FOOD_PATTERNS, t)

    out["pricerange"] = _canon(p, PRICERANGE_VALUES, PRICERANGE_SYNONYMS)
    out["area"]       = _canon(a, AREA_VALUES, AREA_SYNONYMS)
    out["food"]       = _canon(f, FOOD_VALUES, FOOD_SYNONYMS)

    # area phrase fallback
    if out["area"] is None:
        m = re.search(r"\b(in|to|around|near|at|in the)\s+(north|south|east|west|centre|center)\b", t)
        if m:
            out["area"] = _canon(m.group(2), AREA_VALUES, AREA_SYNONYMS)

    return out

def extract_from_file(path: str) -> List[Dict[str, Optional[str]]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    results = []
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s:
            continue
        res = extract_keywords(s)
        res["text"] = s
        results.append(res)
    return results

def extract_auto(input_or_path: str):
    p = Path(input_or_path)
    if p.exists():
        return extract_from_file(str(p))
    return extract_keywords(input_or_path)

# ======= quick demo =======
if __name__ == "__main__":
    samples = [
        "Looking for a moderately priced place in the south serving dasdff."
    ]
    for s in samples:
        print(s, "->", extract_keywords(s))