
import sqlite3

path = r"instance\business_os_backup.db"

connection = sqlite3.connect(path)

print("Integrity:", connection.execute(
    "PRAGMA integrity_check"
).fetchone()[0])

tables = connection.execute(
    "SELECT name FROM sqlite_master WHERE type = ?",
    ("table",)
).fetchall()

print("Tables:")
for table in tables:
    print("-", table[0])

connection.close()
