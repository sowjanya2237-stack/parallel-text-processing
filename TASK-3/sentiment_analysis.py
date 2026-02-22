import pandas as pd
import sqlite3
import re
from datetime import datetime

# -----------------------------------
# KEYWORD LISTS
# -----------------------------------
positive_words = [
    "good", "great", "excellent", "amazing", "love",
    "awesome", "fantastic", "perfect", "nice", "satisfied",
    "delicious", "fresh", "happy"
]

negative_words = [
    "bad", "worst", "poor", "terrible", "hate",
    "awful", "disappointed", "broken", "damaged",
    "stale", "mushy", "expensive"
]

# -----------------------------------
# REGEX PATTERNS
# -----------------------------------
regex_patterns = {

    # NEGATIVE
    r"never\s+buy\s+again": -3,
    r"won'?t\s+buy\s+again": -3,
    r"no\s+flavor": -2,
    r"no\s+taste": -2,
    r"arrived\s+.*melted": -3,
    r"solid\s+mass\s+of\s+melted": -3,
    r"stale": -3,
    r"diarrhea": -3,
    r"itching\s+increased": -3,
    r"too\s+expensive": -2,
    r"not\s+as\s+advertised": -3,
    r"would\s+not\s+buy\s+again": -3,

    # POSITIVE
    r"highly\s+recommend": 3,
    r"definitely\s+recommend": 3,
    r"love\s+this": 2,
    r"very\s+satisfied": 2,
    r"great\s+taste": 2,
    r"delicious": 2,
    r"arrived\s+on\s+time": 2,
    r"works\s+wonders": 3,
    r"great\s+deal": 2,
    r"fresh\s+and\s+delicious": 2,
}

# -----------------------------------
# SENTIMENT CALCULATION
# -----------------------------------
def calculate_sentiment(text):
    score = 0
    text = text.lower()
    words = text.split()

    # Keyword scoring with negation handling
    for i, word in enumerate(words):

        if word in positive_words:
            if i > 0 and words[i - 1] == "not":
                score -= 1
            else:
                score += 1

        if word in negative_words:
            if i > 0 and words[i - 1] == "not":
                score += 1
            else:
                score -= 1

    # Regex scoring
    for pattern, weight in regex_patterns.items():
        if re.search(pattern, text):
            score += weight

    return score


# -----------------------------------
# LABEL ASSIGNMENT (Updated Threshold)
# -----------------------------------
def assign_label(score):
    if score >= 1:
        return "Positive"
    elif score <= -1:
        return "Negative"
    else:
        return "Neutral"


# -----------------------------------
# DATABASE SETUP
# -----------------------------------
def setup_database():
    try:
        conn = sqlite3.connect("sentiment_results.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                score INTEGER,
                sentiment TEXT,
                timestamp TEXT
            )
        """)

        conn.commit()
        return conn, cursor

    except sqlite3.Error as e:
        print("Database Error:", e)
        return None, None


# -----------------------------------
# MAIN FUNCTION
# -----------------------------------
def main():

    try:
        # Load first 2000 rows for faster processing
        df = pd.read_csv("Reviews.csv")
        print("Total Reviews Loaded:", len(df))

    except FileNotFoundError:
        print("Error: Dataset file not found.")
        return
    except Exception as e:
        print("File Error:", e)
        return

    conn, cursor = setup_database()

    if conn is None:
        return

    try:
        results = []

        for _, row in df.iterrows():
            text = str(row["Text"])   # <-- Direct column use

            score = calculate_sentiment(text)
            sentiment = assign_label(score)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            results.append((text, score, sentiment, timestamp))

        cursor.executemany("""
            INSERT INTO results (text, score, sentiment, timestamp)
            VALUES (?, ?, ?, ?)
        """, results)

        conn.commit()
        print("Sentiment analysis completed successfully!")

    except Exception as e:
        print("Processing Error:", e)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
