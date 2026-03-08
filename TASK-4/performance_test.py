import pandas as pd
import sqlite3
import re
import time
from datetime import datetime

# -----------------------------------
# CONFIG
# -----------------------------------
TARGET_ROWS = 1_000_000
DB_NAME = "performance_test.db"

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

regex_patterns = {

    # NEGATIVE
    r"never\s+buy\s+again": -3,
    r"won'?t\s+buy\s+again": -3,
    r"very\s+disappointed": -2,
    r"big\s+disappointment": -3,
    r"not\s+impressed": -2,
    r"taste[s]?\s+awful": -3,
    r"tastes?\s+terrible": -3,
    r"bad\s+taste": -2,
    r"too\s+sweet": -1,
    r"too\s+salty": -1,
    r"too\s+bitter": -2,
    r"stale": -3,
    r"cracked\s+and\s+stale": -3,
    r"not\s+fresh": -2,
    r"expired": -3,
    r"tasted\s+flat": -2,
    r"yuck": -3,
    r"awful": -3,
    r"pathetic": -3,
    r"runny": -2,
    r"waste\s+of\s+money": -3,
    r"avoid\s+this": -3,
    r"aftertaste": -1,

    # POSITIVE
    r"very\s+delicious": 3,
    r"absolutely\s+delicious": 3,
    r"highly\s+recommend": 3,
    r"great\s+taste": 2,
    r"tastes?\s+great": 2,
    r"tastes?\s+good": 2,
    r"excellent": 3,
    r"amazing": 3,
    r"great\s+product": 3,
    r"great\s+value": 2,
    r"good\s+price": 2,
    r"best\s+.*ever": 3,
    r"my\s+favorite": 3,
    r"love\s+this": 3,
    r"love\s+the\s+flavor": 2,
    r"kids?\s+love": 3,
    r"family\s+loves": 3,
    r"very\s+pleased": 2,
    r"perfect\s+taste": 3,
    r"so\s+delicious": 3,
    r"excellent\s+blend": 3,
    r"great\s+snack": 2,
    r"nice\s+flavor": 2,
    r"rich\s+flavor": 2,
    r"aromatic": 2
}

# -----------------------------------
# SENTIMENT CALCULATION
# -----------------------------------
def calculate_sentiment(text):
    score = 0
    text = text.lower()
    words = text.split()

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

    for pattern, weight in regex_patterns.items():
        if re.search(pattern, text):
            score += weight

    return score


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
def setup_database(conn):
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS results")

    cursor.execute("""
        CREATE TABLE results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            score INTEGER,
            sentiment TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()


# -----------------------------------
# INSERT 1 MILLION RECORDS
# -----------------------------------
def process_and_insert(conn):

    cursor = conn.cursor()
    processed = 0
    start_time = time.time()

    for chunk in pd.read_csv(
        "review.csv",
        usecols=["Text"],
        chunksize=10000,
        encoding="latin-1"
    ):

        batch = []

        for text in chunk["Text"]:
            text = str(text)
            score = calculate_sentiment(text)
            sentiment = assign_label(score)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            batch.append((text, score, sentiment, timestamp))
            processed += 1

            if processed >= TARGET_ROWS:
                break

        cursor.executemany("""
            INSERT INTO results (text, score, sentiment, timestamp)
            VALUES (?, ?, ?, ?)
        """, batch)

        conn.commit()

        if processed >= TARGET_ROWS:
            break

    end_time = time.time()

    print(f"\nInserted {processed} records")
    print(f"Processing Time: {end_time - start_time:.2f} seconds")


# -----------------------------------
# QUERY PERFORMANCE TEST
# -----------------------------------
def run_queries(conn, label):

    cursor = conn.cursor()
    timings = {}

    print(f"\n--- Running Queries ({label}) ---")

    # Query 1
    start = time.time()
    cursor.execute("SELECT COUNT(*) FROM results WHERE sentiment='Positive'")
    cursor.fetchone()
    timings["Count Positive"] = time.time() - start
    print("Query 1 (Count Positive):", timings["Count Positive"])

    # Query 2
    start = time.time()
    cursor.execute("SELECT COUNT(*) FROM results WHERE sentiment='Negative'")
    cursor.fetchone()
    timings["Count Negative"] = time.time() - start
    print("Query 2 (Count Negative):", timings["Count Negative"])

    # Query 3
    start = time.time()
    cursor.execute("SELECT * FROM results WHERE score > 3")
    cursor.fetchall()
    timings["Score > 3"] = time.time() - start
    print("Query 3 (Score > 3):", timings["Score > 3"])

    return timings


# -----------------------------------
# APPLY OPTIMIZATION (INDEXING)
# -----------------------------------
def apply_optimization(conn):
    cursor = conn.cursor()

    print("\nApplying Index Optimization...")

    cursor.execute("CREATE INDEX idx_sentiment ON results(sentiment)")
    cursor.execute("CREATE INDEX idx_score ON results(score)")

    conn.commit()


# -----------------------------------
# COMPARE RESULTS & SUMMARY
# -----------------------------------
def compare_results(before, after):

    print("\n========== PERFORMANCE COMPARISON ==========")

    for query in before:
        before_time = before[query]
        after_time = after[query]

        if before_time > 0:
            improvement = ((before_time - after_time) / before_time) * 100
        else:
            improvement = 0

        print(f"\n{query}")
        print(f"Before Optimization : {before_time:.4f} sec")
        print(f"After Optimization  : {after_time:.4f} sec")
        print(f"Performance Improvement : {improvement:.2f}%")



# -----------------------------------
# MAIN
# -----------------------------------
def main():

    conn = sqlite3.connect(DB_NAME)

    print("Setting up database...")
    setup_database(conn)

    print("Processing 1 Million Records...")
    process_and_insert(conn)

    # BEFORE optimization
    before_timings = run_queries(conn, "Before Optimization")

    # Apply indexing
    apply_optimization(conn)

    # AFTER optimization
    after_timings = run_queries(conn, "After Optimization")

    # Compare results
    compare_results(before_timings, after_timings)

    conn.close()


if __name__ == "__main__":
    main()
