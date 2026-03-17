import re
from datetime import datetime

pos_set = {"good", "great", "excellent", "amazing", "love", "awesome", "fantastic", "perfect", "nice", "satisfied", "delicious", "fresh", "happy"}
neg_set = {"bad", "worst", "poor", "terrible", "hate", "awful", "disappointed", "broken", "damaged", "stale", "mushy", "expensive"}

regex_rules = {
    # URGENT
    r"lawsuit": 300, r"suing": 300, r"legal\s+action": 300, r"urgent\s+help": 300,
    r"hospital": 300, r"poisoned": 300, r"allergic\s+reaction": 300, r"choking\s+hazard": 300,
    r"fire\s+hazard": 300, r"reporting\s+to\s+police": 300, r"refund\s+immediately": 300,

    # ABUSIVE
    r"shut\s+up": 200, r"idiot": 200, r"stupid": 200,
    r"pathetic": 200, r"worthless": 200, r"die": 200, r"scum": 200, r"garbage\s+person": 200,
    r"hate\s+you": 200, r"moron": 200, r"dumb": 200,

    # SPAM
    r"click\s+here": 100, r"buy\s+now": 100, r"promo\s+code": 100, r"http\S+": 100,
    r"www\.\S+": 100, r"bitcoin": 100, r"crypto": 100, r"earn\s+money": 100,
    r"free\s+iphone": 100, r"lottery\s+winner": 100, r"whatsapp\s+me": 100, r"telegram": 100,

    # SUGGESTION
    r"i\s+suggest": 50, r"should\s+add": 50, r"feature\s+request": 50,
    r"would\s+be\s+better": 50, r"please\s+improve": 50, r"consider\s+adding": 50,
    r"missing\s+a\s+feature": 50, r"can\s+you\s+make": 50, r"it\s+would\s+be\s+great\s+if": 50,

    # NEGATIVE
    r"very\s+flimsy": -3, r"cheap(ly)?\s+made": -3, r"parts\s+missing": -3,
    r"came\s+with\s+parts\s+missing": -3, r"wont\s+stick": -3, r"won'?t\s+stick": -3,
    r"does\s+not\s+capture": -2, r"screen\s+protector\s+crack": -3, r"fur\s+started\s+falling\s+out": -3,
    r"lead\s+.*\s+fragile": -3, r"prone\s+to\s+breaking": -3, r"broke\s+easily": -3,
    r"leak(s|ing)?": -3, r"stinks?\s+bad": -3, r"very\s+bulky": -2, r"not\s+very\s+warm": -2,
    r"disappointed": -2, r"waste\s+your\s+money": -3, r"not\s+recommend": -3,
    r"made\s+my\s+dog\s+.*\s+worse": -3, r"dogs?\s+diarrhea": -3, r"didn'?t\s+work": -3,
    r"brittle": -3, r"full\s+of\s+cracks": -3,

    # POSITIVE
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

# --- COMPILED REGEX ENGINE ---
COMBINED_PATTERN = re.compile(
    '|'.join(f'(?P<r{i}>{p})' for i, p in enumerate(regex_rules.keys())),
    re.IGNORECASE
)

WEIGHT_MAP = {f'r{i}': weight for i, weight in enumerate(regex_rules.values())}


# OPTIMIZED FULL-SCAN FUNCTION
def analyze_chunk(chunk_data):
    start_idx, lines = chunk_data
    results = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for i, text in enumerate(lines):
        score = 0
        category = None

        text_lower = text.lower() if isinstance(text, str) else str(text).lower()

        # FULL REGEX SCAN
        highest_priority = 0

        for match in COMBINED_PATTERN.finditer(text_lower):
            w = WEIGHT_MAP[match.lastgroup]

            if w >= 50:
                if w > highest_priority:
                    highest_priority = w
            else:
                score += w

        # CATEGORY DECISION AFTER FULL SCAN
        if highest_priority:
            category = "Urgent" if highest_priority == 300 else \
                    "Abusive" if highest_priority == 200 else \
                    "Spam" if highest_priority == 100 else \
                    "Suggestion"
        else:
            pos_count = 0
            neg_count = 0

            # CHECK EVERY WORD
            for word in text_lower.split():
                if word in pos_set:
                    pos_count += 1
                elif word in neg_set:
                    neg_count += 1

            score += pos_count - neg_count

            category = "Positive" if score >= 1 else "Negative" if score <= -1 else "Neutral"

        results.append((start_idx + i, score, category, ts))

    return results