
from pathlib import Path
import sqlite3
import shutil

project_dir = Path(__file__).resolve().parent
instance_dir = project_dir / "instance"
active_db = instance_dir / "business_os.db"
backup_db = instance_dir / "business_os_backup.db"

# Verify the backup before changing anything.
if not backup_db.exists():
    raise FileNotFoundError(
        f"Valid backup not found: {backup_db}"
    )

with sqlite3.connect(str(backup_db)) as connection:
    result = connection.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]

if result != "ok":
    raise RuntimeError("Backup is invalid. Stopping.")

# Preserve the invalid active file rather than deleting it.
if active_db.exists():
    damaged_db = instance_dir / "business_os_invalid_old.db"

    if damaged_db.exists():
        raise FileExistsError(
            f"{damaged_db} already exists. "
            "Do not overwrite it."
        )

    shutil.move(str(active_db), str(damaged_db))
    print(f"Preserved old database at: {damaged_db}")

# Import only after moving the invalid database.
from app import app
from models import db

with app.app_context():
    db.create_all()

print("Fresh database created successfully.")
print("Your old backup and invalid database are preserved.")
print("You can now register a new account.")
