import os
import time
from multiprocessing import Pool


def process_file(filename):
    print(f"Processing {filename}", flush=True)

    with open(filename, "r", encoding="utf-8") as f:
        data = f.read().lower()

    score = 0

    # Scoring rules
    if "excellent" in data:
        score += 3

    if "disappointing" in data:
        score -= 2

    if "happy" in data:
        score += 2

    if "delay" in data:
        score -= 2

    time.sleep(1)  # simulate processing

    print(f"Finished {filename}", flush=True)

    return score


if __name__ == "__main__":

    files = [f for f in os.listdir() if f.endswith(".txt")]

    if not files:
        print("No text files found.")
        exit()

    # ===== SINGLE PROCESS EXECUTION =====
    print("===== SINGLE PROCESS EXECUTION =====")
    start_single = time.time()

    total_single_score = 0
    for file in files:
        total_single_score += process_file(file)

    end_single = time.time()
    single_time = end_single - start_single


    # ===== MULTI-PROCESS EXECUTION =====
    print("\n===== MULTI-PROCESS EXECUTION =====")
    start_multi = time.time()

    with Pool() as p:
        scores = p.map(process_file, files)

    total_multi_score = sum(scores)

    end_multi = time.time()
    multi_time = end_multi - start_multi

    print(f"Multi Process Time: {multi_time:.2f} seconds")


    # ===== TOTAL SCORE =====
    print("\n======TOTAL SCORE======")
    print(f"Total Score: {total_multi_score}")



    # ===== COMPARISON =====
    print("\n======COMPARISON======")
    print(f"Single Process Time: {single_time:.2f} seconds")
    print(f"Multi Process Time: {multi_time:.2f} seconds")
