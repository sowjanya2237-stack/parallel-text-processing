import re
from datetime import datetime

pos_set = {
    "good","great","excellent","amazing","love","awesome",
    "fantastic","perfect","nice","satisfied","delicious",
    "fresh","happy"
}

neg_set = {
    "bad","worst","poor","terrible","hate","awful",
    "disappointed","broken","damaged","stale",
    "mushy","expensive"
}

# REGEX RULES
URGENT_RE = re.compile(
    r"lawsuit|suing|legal\s+action|urgent\s+help|hospital|poisoned|allergic\s+reaction|choking\s+hazard|fire\s+hazard|reporting\s+to\s+police|refund\s+immediately",
    re.IGNORECASE
)

ABUSIVE_RE = re.compile(
    r"shut\s+up|idiot|stupid|pathetic|worthless|die|scum|garbage\s+person|hate\s+you|moron|dumb",
    re.IGNORECASE
)

SPAM_RE = re.compile(
    r"click\s+here|buy\s+now|promo\s+code|http\S+|www\.\S+|bitcoin|crypto|earn\s+money|free\s+iphone|lottery\s+winner|whatsapp\s+me|telegram",
    re.IGNORECASE
)

SUGGEST_RE = re.compile(
    r"i\s+suggest|should\s+add|feature\s+request|would\s+be\s+better|please\s+improve|consider\s+adding|missing\s+a\s+feature|can\s+you\s+make|it\s+would\s+be\s+great\s+if",
    re.IGNORECASE
)

# POSITIVE PATTERNS
POS_PATTERNS = [
    (r"super\s+smooth", 2), (r"very\s+yummy", 2), (r"perfect\s+for\s+kombucha", 2),
    (r"fits\s+perfectly", 3), (r"light\s+weight", 2), (r"very\s+pigmented", 2),
    (r"very\s+strong", 2), (r"resist\s+breaking", 2), (r"love\s+this", 3), (r"i\s+love\s+this", 3),
    (r"highly\s+recommend", 3), (r"dog\s+loves\s+it", 3), (r"my\s+dog\s+loves", 3),
    (r"cats?\s+loves?", 3), (r"kids\s+love\s+it", 3), (r"good\s+quality", 2),
    (r"great\s+quality", 3), (r"fast\s+shipping", 2), (r"works\s+great", 3),
    (r"worked\s+perfectly", 3), (r"great\s+product", 3), (r"nice\s+product", 2),
    (r"nice\s+pens", 2), (r"great\s+deal", 2), (r"excellent\s+quality", 3),
    (r"easy\s+to\s+use", 2), (r"easy\s+to\s+clean", 2), (r"very\s+cute", 2),
    (r"perfect\s+fit", 3), (r"protected\s+the\s+phone", 2), (r"great\s+protection", 2),
    (r"tastes?\s+great", 2), (r"delicious", 2)
]

POS_REGEX = [(re.compile(p, re.IGNORECASE), w) for p, w in POS_PATTERNS]

# NEGATIVE PATTERNS
NEG_PATTERNS = [
    (r"very\s+flimsy", -3), (r"cheap(ly)?\s+made", -3), (r"parts\s+missing", -3),
    (r"came\s+with\s+parts\s+missing", -3), (r"wont\s+stick", -3), (r"won'?t\s+stick", -3),
    (r"does\s+not\s+capture", -2), (r"screen\s+protector\s+crack", -3), (r"fur\s+started\s+falling\s+out", -3),
    (r"lead\s+.*\s+fragile", -3), (r"prone\s+to\s+breaking", -3), (r"broke\s+easily", -3),
    (r"leak(s|ing)?", -3), (r"stinks?\s+bad", -3), (r"very\s+bulky", -2), (r"not\s+very\s+warm", -2),
    (r"disappointed", -2), (r"waste\s+your\s+money", -3), (r"not\s+recommend", -3),
    (r"made\s+my\s+dog\s+.*\s+worse", -3), (r"dogs?\s+diarrhea", -3), (r"didn'?t\s+work", -3),
    (r"brittle", -3), (r"full\s+of\s+cracks", -3)
]

NEG_REGEX = [(re.compile(p, re.IGNORECASE), w) for p, w in NEG_PATTERNS]

# MAIN FUNCTION
def analyze_chunk(chunk_data):
    start_idx, lines = chunk_data
    results = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for i, text in enumerate(lines):
        score, category = 0, None
        text_lower = str(text).lower()

        if len(text_lower) < 3:
            results.append((start_idx + i, 0, "Neutral", ts))
            continue

        # STEP 1: SENTIMENT
        pos_hits = 0
        neg_hits = 0

        for w in text_lower.split():
            if w in pos_set:
                pos_hits += 1
            elif w in neg_set:
                neg_hits += 1

        score = pos_hits - neg_hits

        #  STEP 2: DECISION
        if score != 0:
            category = "Positive" if score > 0 else "Negative"
            results.append((start_idx + i, score, category, ts))
            continue

        # STEP 3: PRIORITY CATEGORY
        if URGENT_RE.search(text_lower):
            category = "Urgent"

        elif ABUSIVE_RE.search(text_lower):
            category = "Abusive"

        elif SPAM_RE.search(text_lower):
            category = "Spam"

        elif SUGGEST_RE.search(text_lower):
            category = "Suggestion"

        # STEP 4: REGEX SENTIMENT
        if not category:
            # POSITIVE
            for pattern, weight in POS_REGEX:
                if pattern.search(text_lower):
                    score += weight
                    category = "Positive"
                    break

        if not category:
            # NEGATIVE
            for pattern, weight in NEG_REGEX:
                if pattern.search(text_lower):
                    score += weight
                    category = "Negative"
                    break

        if not category:
            category = "Neutral"

        results.append((start_idx + i, score, category, ts))

    return results