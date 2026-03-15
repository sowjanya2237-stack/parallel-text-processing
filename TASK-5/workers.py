import re
from datetime import datetime

pos_set = {"good", "great", "excellent", "amazing", "love", "awesome", "fantastic", "perfect", "nice", "satisfied", "delicious", "fresh", "happy"}
neg_set = {"bad", "worst", "poor", "terrible", "hate", "awful", "disappointed", "broken", "damaged", "stale", "mushy", "expensive"}

# --- MASTER REGEX RULES ---
regex_rules = {
    # URGENT
    r"lawsuit": 300, r"suing": 300, r"legal\s+action": 300, r"urgent\s+help": 300,
    # TOXIC
    r"shut\s+up": 200, r"idiot": 200, r"stupid": 200, r"f\*\*\*": 200, r"s\*\*\*": 200,
    # SPAM
    r"click\s+here": 100, r"buy\s+now": 100, r"promo\s+code": 100, r"http\S+": 100,
    # SUGGESTION
    r"i\s+suggest": 50, r"should\s+add": 50, r"feature\s+request": 50,

    # NEGATIVE
    r"very\s+flimsy": -3,
    r"cheap(ly)?\s+made": -3,
    r"parts\s+missing": -3,
    r"came\s+with\s+parts\s+missing": -3,
    r"wont\s+stick": -3,
    r"won'?t\s+stick": -3,
    r"does\s+not\s+capture": -2,
    r"screen\s+protector\s+crack": -3,
    r"fur\s+started\s+falling\s+out": -3,
    r"lead\s+.*\s+fragile": -3,
    r"prone\s+to\s+breaking": -3,
    r"broke\s+easily": -3,
    r"leak(s|ing)?": -3,
    r"stinks?\s+bad": -3,
    r"very\s+bulky": -2,
    r"not\s+very\s+warm": -2,
    r"disappointed": -2,
    r"waste\s+your\s+money": -3,
    r"not\s+recommend": -3,
    r"made\s+my\s+dog\s+.*\s+worse": -3,
    r"dogs?\s+diarrhea": -3,
    r"didn'?t\s+work": -3,
    r"brittle": -3,
    r"full\s+of\s+cracks": -3,

    # POSITIVE
    r"super\s+smooth": 2,
    r"very\s+yummy": 2,
    r"perfect\s+for\s+kombucha": 2,
    r"fits\s+perfectly": 3,
    r"light\s+weight": 2,
    r"very\s+pigmented": 2,
    r"very\s+strong": 2,
    r"resist\s+breaking": 2,
    r"love\s+this": 3,
    r"i\s+love\s+this": 3,
    r"highly\s+recommend": 3,
    r"dog\s+loves\s+it": 3,
    r"my\s+dog\s+loves": 3,
    r"cats?\s+loves?": 3,
    r"kids\s+love\s+it": 3,
    r"good\s+quality": 2,
    r"great\s+quality": 3,
    r"fast\s+shipping": 2,
    r"works\s+great": 3,
    r"worked\s+perfectly": 3,
    r"great\s+product": 3,
    r"nice\s+product": 2,
    r"nice\s+pens": 2,
    r"great\s+deal": 2,
    r"excellent\s+quality": 3,
    r"easy\s+to\s+use": 2,
    r"easy\s+to\s+clean": 2,
    r"very\s+cute": 2,
    r"perfect\s+fit": 3,
    r"protected\s+the\s+phone": 2,
    r"great\s+protection": 2,
    r"tastes?\s+great": 2,
    r"delicious": 2
}

COMBINED_PATTERN = re.compile('|'.join(f'(?P<r{i}>{p})' for i, p in enumerate(regex_rules.keys())), re.IGNORECASE)
WEIGHT_MAP = {f'r{i}': weight for i, weight in enumerate(regex_rules.values())}

def analyze_chunk(chunk):
    """Worker function optimized for high-volume text analysis"""
    results = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for text in chunk:
        score = 0
        text_lower = str(text).lower()
        category = None
        
        # 1. SCAN REGEX (Priority Tags & Specific Sentiment Phrases)
        for match in COMBINED_PATTERN.finditer(text_lower):
            weight = WEIGHT_MAP[match.lastgroup]
            
            # Categorization takes priority
            if weight == 300: category = "Urgent"; break
            if weight == 200: category = "Toxic"; break
            if weight == 100: category = "Spam"; break
            if weight == 50:  category = "Suggestion"; break
            
            # Otherwise, accumulate sentiment score
            score += weight
        
        if category:
            results.append((0, category, ts))
            continue

        # 2. KEYWORD SCORING (Set Mathematics)
        words = set(text_lower.split())
        score += len(words & pos_set)
        score -= len(words & neg_set)
        
        # 3. FINAL LABELING
        label = "Positive" if score >= 1 else "Negative" if score <= -1 else "Neutral"
        results.append((score, label, ts))
        
    return results