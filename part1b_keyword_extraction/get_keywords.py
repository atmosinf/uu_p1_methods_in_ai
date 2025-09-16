import csv
import re
import unicodedata
from pathlib import Path
from typing import Dict, Optional, Set, Tuple, Callable, List

# ---------- Helpers ----------

def _norm(s: str) -> str:
    """Lowercase, remove accents, collapse whitespace, strip punctuation at ends."""
    s = s.lower()
    s = "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))
    s = re.sub(r"[^\w\s'&/-]+", " ", s)   # keep word-ish chars and a few joiners
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _compile_phrase_regex(phrases: Set[str]) -> List[Tuple[str, re.Pattern]]:
    """
    Compile word-boundary regexes for each phrase.
    Sort by length (desc) so longer phrases match first.
    """
    cleaned = sorted({_norm(p) for p in phrases if p and _norm(p)}, key=len, reverse=True)
    patterns = []
    for p in cleaned:
        # word-boundary on both sides; allow internal spaces & symbols we normalized to spaces
        # Use (?i) for case-insensitive while preserving original text if needed later.
        pat = re.compile(rf"(?i)\b{re.escape(p)}\b")
        patterns.append((p, pat))
    return patterns

def _apply_synonyms(value: str, synonyms: Dict[str, str]) -> str:
    key = _norm(value)
    return synonyms.get(key, key)

# ---------- Loader ----------

def load_catalog(csv_path: str) -> Dict[str, Set[str]]:
    """
    Reads restaurant_info.csv and returns sets for 'pricerange', 'area', 'food'.
    Column names are matched case-insensitively.
    """
    csv_path = str(Path(csv_path))
    fields = {"pricerange": set(), "area": set(), "food": set()}

    # Try header-based reading; fall back to position if needed
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Map case-insensitively
        lower_map = {k.lower(): k for k in reader.fieldnames or []}
        col_price = lower_map.get("pricerange")
        col_area  = lower_map.get("area")
        col_food  = lower_map.get("food")

        if not (col_price and col_area and col_food):
            raise ValueError("CSV must contain columns: pricerange, area, food")

        for row in reader:
            if row.get(col_price): fields["pricerange"].add(str(row[col_price]).strip())
            if row.get(col_area):  fields["area"].add(str(row[col_area]).strip())
            if row.get(col_food):  fields["food"].add(str(row[col_food]).strip())

    # Normalize display sets (store original spellings too, but we'll match on normalized)
    # Return as-is; matching uses normalized copies internally.
    return fields

# ---------- Extractor factory ----------

def build_keyword_extractor(csv_path: str) -> Callable[[str], Dict[str, Optional[str]]]:
    catalog = load_catalog(csv_path)

    # Synonyms / normalizations (extend as needed)
    pricerange_syn = {
        "moderately priced": "moderate",
        "moderately": "moderate",
        "mid": "moderate",
        "midrange": "moderate",
        "mid-range": "moderate",
        "affordable": "moderate",
        "budget": "cheap",
        "low": "cheap",
        "inexpensive": "cheap",
        "pricey": "expensive",
        "high end": "expensive",
        "high-end": "expensive",
        "any": "dontcare",
        "any price": "dontcare",
        "dont care": "dontcare",
        "don't care": "dontcare",
        "doesnt matter": "dontcare",
        "doesn't matter": "dontcare",
    }

    area_syn = {
        "center": "centre",
        "city center": "centre",
        "city centre": "centre",
        "downtown": "centre",
        "any": "dontcare",
        "anywhere": "dontcare",
        "dont care": "dontcare",
        "don't care": "dontcare",
        "doesnt matter": "dontcare",
        "doesn't matter": "dontcare",
    }

    food_syn = {
        # common variants seen in dialogs
        "asian oriental": "asian oriental",
        "gastropub": "gastropub",
        "venetian": "venetian",   # may not exist in CSV; still allow detection if present in text
        "europe": "european",
        "britain": "british",
        "portugese": "portuguese",  # misspelling
    }

    # Build normalized value sets from CSV + synonyms keys, so we can match both
    price_values = { _apply_synonyms(v, pricerange_syn) for v in catalog["pricerange"] }
    area_values  = { _apply_synonyms(v, area_syn) for v in catalog["area"] }
    food_values  = { _apply_synonyms(v, food_syn) for v in catalog["food"] }

    # Add the *keys* of synonyms to candidate phrase lists, so input like "high-end" matches
    price_candidates = price_values.union(set(pricerange_syn.keys()))
    area_candidates  = area_values.union(set(area_syn.keys()))
    food_candidates  = food_values.union(set(food_syn.keys()))

    price_patterns = _compile_phrase_regex(price_candidates)
    area_patterns  = _compile_phrase_regex(area_candidates)
    food_patterns  = _compile_phrase_regex(food_candidates)

    # Map normalized → canonical (prefer CSV canonical if possible)
    def _canonicalize(value: str, known_values: Set[str], syn: Dict[str, str]) -> str:
        v = _apply_synonyms(value, syn)
        # If CSV includes 'dontcare' under any column, keep it; else pass through
        if v in known_values:
            return v
        # try to map to a best-known alias (e.g., 'centre' if 'center' seen)
        # if not present, just return normalized v
        return v

    def extract(text: str) -> Dict[str, Optional[str]]:
        norm_text = _norm(text)

        result = {"pricerange": None, "area": None, "food": None}

        # helper to match first pattern that appears (longest phrases first)
        def find_first(patterns: List[Tuple[str, re.Pattern]]) -> Optional[str]:
            for phrase, pat in patterns:
                if pat.search(norm_text):
                    return phrase
            return None

        # pricerange
        p = find_first(price_patterns)
        if p is not None:
            result["pricerange"] = _canonicalize(p, price_values, pricerange_syn)

        # area
        a = find_first(area_patterns)
        if a is not None:
            result["area"] = _canonicalize(a, area_values, area_syn)

        # food (allow multiple mentions but take the first longest match)
        f = find_first(food_patterns)
        if f is not None:
            result["food"] = _canonicalize(f, food_values, food_syn)

        # Special handling for common phrasings:
        # e.g., "in the north part of town" → area=north
        m = re.search(r"\b(in|to|around|near|at|in the)\s+(north|south|east|west|centre|center)\b", norm_text)
        if m and not result["area"]:
            result["area"] = _canonicalize(m.group(2), area_values, area_syn)

        # "moderately priced", "cheap place", etc., already covered via synonyms and regexes.

        return result

    return extract

# ---------- Quick example ----------
if __name__ == "__main__":
    # Point this to your uploaded file path
    csv_path = "restaurant_info.csv"
    extract_keywords = build_keyword_extractor(csv_path)

    tests = [
        "I'm looking for a moderately priced place in the south serving bistro food.",
        "Any area is fine, I want cheap italian.",
        "Find me an EXPENSIVE restaurant in the center. Food doesn't matter.",
        "Do you have asian oriental in the west?",
        "a cheap place, don't care about area, maybe british"
    ]
    for t in tests:
        print(t, "→", extract_keywords(t))