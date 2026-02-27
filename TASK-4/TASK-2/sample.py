import sqlite3

# Connect
conn = sqlite3.connect("textdb.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS file_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    score INTEGER
)
""")
conn.commit()

# Insert example data
cursor.execute(
    "INSERT INTO file_scores (filename, score) VALUES (?, ?)",
    ("sample.txt", 5)
)
conn.commit()

# View data
cursor.execute("SELECT * FROM file_scores")
rows = cursor.fetchall()

for row in rows:
    print(row)

cursor.close()
conn.close()
