import csv
import re
import unicodedata
from pathlib import Path
from typing import Dict, Optional, Set, Tuple, Callable, List

# ---------- Text utils ----------

def _norm(s: str) -> str:
    """Lowercase, remove accents, collapse whitespace, strip punctuation at ends."""
    s = s.lower()
    s = "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))
    s = re.sub(r"[^\w\s'&/-]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _compile_phrase_regex(phrases: Set[str]) -> List[Tuple[str, re.Pattern]]:
    """
    Compile boundary-aware regexes for each phrase.
    Sort by length (desc) so longer phrases match first.
    """
    cleaned = sorted({_norm(p) for p in phrases if p and _norm(p)}, key=len, reverse=True)
    patterns = []
    for p in cleaned:
        patterns.append((p, re.compile(rf"(?i)\b{re.escape(p)}\b")))
    return patterns

def _apply_synonyms(value: str, synonyms: Dict[str, str]) -> str:
    key = _norm(value)
    return synonyms.get(key, key)

# ---------- Data loaders ----------

def load_catalog(csv_path: str) -> Dict[str, Set[str]]:
    """
    Reads restaurant_info.csv and returns sets for 'pricerange', 'area', 'food'.
    """
    csv_path = str(Path(csv_path))
    fields = {"pricerange": set(), "area": set(), "food": set()}

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        lower_map = {k.lower(): k for k in (reader.fieldnames or [])}
        col_price = lower_map.get("pricerange")
        col_area  = lower_map.get("area")
        col_food  = lower_map.get("food")
        if not (col_price and col_area and col_food):
            raise ValueError("CSV must contain columns: pricerange, area, food")

        for row in reader:
            if row.get(col_price): fields["pricerange"].add(str(row[col_price]).strip())
            if row.get(col_area):  fields["area"].add(str(row[col_area]).strip())
            if row.get(col_food):  fields["food"].add(str(row[col_food]).strip())
    return fields

def load_dialog_keywords(dialogs_path: str) -> Dict[str, Set[str]]:
    """
    Parses all_dialogs.txt and collects values for pricerange/area/food from 'speech act:' annotations.
    Accepts patterns like:
      - inform(food=thai) / request(food) / confirm(pricerange=moderate, ...)
      - '... =dontcare' or 'pricerange=dontcare'
    """
    dialogs_path = str(Path(dialogs_path))
    found = {"pricerange": set(), "area": set(), "food": set()}

    # Regex to catch key=value inside parentheses for relevant keys
    kv_pat = re.compile(r"\b(pricerange|area|food)\s*=\s*([^) ,|]+)", re.IGNORECASE)
    # Also capture quoted multiword foods e.g., food="asian oriental"
    kv_quote_pat = re.compile(r'\b(pricerange|area|food)\s*=\s*"([^"]+)"', re.IGNORECASE)

    with open(dialogs_path, encoding="utf-8") as f:
        for line in f:
            if "speech act:" not in line.lower():
                continue

            # quoted values first (multiword)
            for k, v in kv_quote_pat.findall(line):
                found[k.lower()].add(v.strip())

            # unquoted values (single-token)
            for k, v in kv_pat.findall(line):
                v = v.strip()
                # skip placeholders like request(food) without value
                if v and v not in {")", "(", ","}:
                    found[k.lower()].add(v)

    # Clean trivial tokens that are not values (e.g., 'type' might sneak in from malformed lines)
    for k in found:
        cleaned = set()
        for v in found[k]:
            nv = _norm(v)
            if nv and nv not in {"food", "type", "task", "addr", "phone", "postcode"}:
                cleaned.add(nv)
        found[k] = cleaned

    return found

# ---------- Extractor factory ----------

def build_keyword_extractor(csv_path: str, dialogs_path: Optional[str] = None) -> Callable[[str], Dict[str, Optional[str]]]:
    catalog = load_catalog(csv_path)

    # Seed with CSV values
    price_values = {_norm(v) for v in catalog["pricerange"]}
    area_values  = {_norm(v) for v in catalog["area"]}
    food_values  = {_norm(v) for v in catalog["food"]}

    # Mine extra values from dialogs (if provided)
    if dialogs_path:
        mined = load_dialog_keywords(dialogs_path)
        price_values |= {_norm(v) for v in mined["pricerange"]}
        area_values  |= {_norm(v) for v in mined["area"]}
        food_values  |= {_norm(v) for v in mined["food"]}

    # Synonym maps / normalizations (extend freely)
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
        # common phrases
        "north part of town": "north",
        "south part of town": "south",
        "east part of town": "east",
        "west part of town": "west",
    }
    food_syn = {
        "europe": "european",
        "britain": "british",
        "portugese": "portuguese",
        "gastro pub": "gastropub",
        "asian-oriental": "asian oriental",
        "asian/oriental": "asian oriental",
    }

    # Add synonym KEYS to candidate lists so variant strings match
    price_candidates = price_values.union(set(pricerange_syn.keys()))
    area_candidates  = area_values.union(set(area_syn.keys()))
    food_candidates  = food_values.union(set(food_syn.keys()))

    price_patterns = _compile_phrase_regex(price_candidates)
    area_patterns  = _compile_phrase_regex(area_candidates)
    food_patterns  = _compile_phrase_regex(food_candidates)

    def _canonicalize(value: str, known_values: Set[str], syn: Dict[str, str]) -> str:
        v = _apply_synonyms(value, syn)
        return v if v in known_values or v == "dontcare" else v

    def extract(text: str) -> Dict[str, Optional[str]]:
        norm_text = _norm(text)
        result = {"pricerange": None, "area": None, "food": None}

        def find_first(patterns: List[Tuple[str, re.Pattern]]) -> Optional[str]:
            for phrase, pat in patterns:
                if pat.search(norm_text):
                    return phrase
            return None

        # Direct matches
        p = find_first(price_patterns)
        a = find_first(area_patterns)
        f = find_first(food_patterns)

        if p is not None:
            result["pricerange"] = _canonicalize(p, price_values, pricerange_syn)
        if a is not None:
            result["area"] = _canonicalize(a, area_values, area_syn)
        if f is not None:
            result["food"] = _canonicalize(f, food_values, food_syn)

        # Phrasey area fallback: "in the north/south/east/west/centre"
        m = re.search(r"\b(in|to|around|near|at|in the)\s+(north|south|east|west|centre|center)\b", norm_text)
        if m and not result["area"]:
            result["area"] = _canonicalize(m.group(2), area_values, area_syn)

        # Accept "any/doesn't matter/don't care" declarations per slot
        if result["pricerange"] is None and re.search(r"\b(any price|any|dont'? care|doesn'?t matter)\b", norm_text):
            result["pricerange"] = "dontcare" if "price" in norm_text or "range" in norm_text else result["pricerange"]
        if result["area"] is None and re.search(r"\b(anywhere|any|dont'? care|doesn'?t matter)\b", norm_text):
            result["area"] = "dontcare"
        if result["food"] is None and re.search(r"\b(any( (kind|type) of)? food|dont'? care|doesn'?t matter)\b", norm_text):
            result["food"] = "dontcare"

        return result

    return extract

# ---------- Quick example ----------
if __name__ == "__main__":
    csv_path = "restaurant_info.csv"
    dialogs_path = "all_dialogs.txt"
    extract_keywords = build_keyword_extractor(csv_path, dialogs_path)

    tests = [
        "I'm after a moderately priced spot in the south serving bistro.",
        "Any area is fine; give me cheap italian.",
        "Find an EXPENSIVE place in the center (food doesn't matter).",
        "Do you have asian oriental in the west?",
        "north part of town, don't care about food, mid-range price.",
        "either venetian or gastropub, any price, anywhere",
    ]
    tests1 = [
        "I'm looking for world food",
        "I want a restaurant that serves world food",
        "I want a restaurant serving Swedish food",
        "I'm looking for a restaurant in the center",
        "I would like a cheap restaurant in the west part of town",
        "I'm looking for a moderately priced restaurant in the west part of town",
        "I'm looking for a restaurant in any area that serves Tuscan food",
        "Can I have an expensive restaurant",
        "I'm looking for an expensive restaurant and it should serve international food",
        "I need a Cuban restaurant that is moderately priced",
        "I'm looking for a moderately priced restaurant with Catalan food",
        "What is a cheap restaurant in the south part of town",
        "What about Chinese food",
        "I wanna find a cheap restaurant",
        "I'm looking for Persian food please",
        "Find a Cuban restaurant in the center"
    ]
    samples = [
        "Looking for a moderately priced place in the south serving bistro.",
        "Any area is fine; give me cheap italian.",
        "Find an EXPENSIVE place in the center; food doesn't matter.",
        "Do you have asian oriental in the west?",
        "north part of town, don't care about food, mid-range price.",
        "either venetian or gastropub, any price, anywhere",
    ]
    for t in samples:
        print(t, "→", extract_keywords(t))