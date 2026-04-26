import sqlite3

conn = sqlite3.connect("dev.db")
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables found:", len(tables))
for t in tables:
    print(" -", t[0])
conn.close()