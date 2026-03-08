# workers.py
import re
from datetime import datetime

# Pre-defined sets for O(1) instant lookup
pos_set = {"good", "great", "excellent", "amazing", "love", "awesome", "fantastic", "perfect", "nice", "satisfied", "delicious", "fresh", "happy"}
neg_set = {"bad", "worst", "poor", "terrible", "hate", "awful", "disappointed", "broken", "damaged", "stale", "mushy", "expensive"}

# Regex Rules
regex_rules = {
    r"very\s+flimsy": -3, r"cheap(ly)?\s+made": -3, r"parts\s+missing": -3,
    r"came\s+with\s+parts\s+missing": -3, r"wont\s+stick": -3, r"won'?t\s+stick": -3,
    r"does\s+not\s+capture": -2, r"screen\s+protector\s+crack": -3, r"fur\s+started\s+falling\s+out": -3,
    r"lead\s+.*\s+fragile": -3, r"prone\s+to\s+breaking": -3, r"broke\s+easily": -3,
    r"leak(s|ing)?": -3, r"stinks?\s+bad": -3, r"very\s+bulky": -2, r"not\s+very\s+warm": -2,
    r"disappointed": -2, r"waste\s+your\s+money": -3, r"not\s+recommend": -3,
    r"made\s+my\s+dog\s+.*\s+worse": -3, r"dogs?\s+diarrhea": -3, r"didn'?t\s+work": -3,
    r"brittle": -3, r"full\s+of\s+cracks": -3,
    r"super\s+smooth": 2, r"very\s+yummy": 2, r"perfect\s+for\s+kombucha": 2,
    r"fits\s+perfectly": 3, r"light\s+weight": 2, r"very\s+pigmented": 2,
    r"very\s+strong": 2, r"resist\s+breaking": 2, r"love\s+this": 3, r"i\s+love\s+this": 3,
    r"highly\s+recommend": 3, r"dog\s+loves\s+it": 3, r"my\s+dog\s+loves": 3,
    r"cats?\s+loves?": 3, r"kids\s+love\s+it": 3, r"good\s+quality": 2,
    r"great\s+quality": 3, r"fast\s+shipping": 2, r"works\s+great": 3,
    r"worked\s+perfectly": 3, r"great\s+product": 3, r"nice\s+product": 2,
    r"nice\s+pens": 2, r"great\s+deal": 2, r"excellent\s+quality": 3,
    r"easy\s+to\s+use": 2, r"easy\s+to\s+clean": 2, r"very\s+cute": 2,
    r"perfect\s+fit": 3, r"protected\s+the\s+phone": 2, r"great\s+protection": 2,
    r"tastes?\s+great": 2, r"delicious": 2
}

def analyze_chunk(chunk):
    """Parallel process worker for text scoring"""
    batch_results = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    compiled = [(re.compile(p, re.IGNORECASE), w) for p, w in regex_rules.items()]
    
    for text in chunk:
        score = 0
        text_lower = str(text).lower()
        for pattern, weight in compiled:
            if pattern.search(text_lower):
                score += weight
        words = text_lower.split()
        for i, word in enumerate(words):
            if word in pos_set:
                score += -1 if (i > 0 and words[i-1] == "not") else 1
            elif word in neg_set:
                score += 1 if (i > 0 and words[i-1] == "not") else -1
        label = "Positive" if score >= 1 else "Negative" if score <= -1 else "Neutral"
        
        # FIXED: Removed '[:150]' so full text is stored
        batch_results.append((text, score, label, ts)) 
    return batch_results