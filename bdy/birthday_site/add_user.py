import sqlitecloud
import ssl

# Try with sqlitecloud:// prefix
SQLITECLOUD_URL = "sqlitecloud://cqmi27ahvz.g1.sqlite.cloud:8860/auth.sqlitecloud?apikey=68YHWVUrrEiaBFOMxPLq7klsnQ9YhDLNSESQc5HpmLc"

# Connect and add user
db = sqlitecloud.connect(SQLITECLOUD_URL)

# Create table if not exists
db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
""")

# Add your user (change username/password)
try:
    db.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        ("sanjana", "sanju123")  # ← Change these
    )
    print("✅ User added successfully!")
except Exception as e:
    print(f"⚠️ {e}")

db.commit()
db.close()