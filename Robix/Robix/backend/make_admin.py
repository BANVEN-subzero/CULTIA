
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "cultureAI", "data", "cultia.db")
# Or whatever your DB path is! Adjust if needed!

def make_admin(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET role = 'admin' WHERE username = ?", (username,))
        conn.commit()
        print(f"User {username} is now an admin!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        make_admin(sys.argv[1])
    else:
        print("Usage: python make_admin.py <username>")
