import sqlite3
import os
import threading

db_lock = threading.Lock()  # Thread lock to prevent database locking issues

def view_users():
    """View all users in the database"""
    db_path = os.path.join(os.path.dirname(__file__), 'users.db')
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
    
    try:
        with db_lock:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get column names
            cursor.execute("PRAGMA table_info(users)")
            columns = [info[1] for info in cursor.fetchall()]
            
            # Get all users
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            print("\n" + "="*80)
            print("DATABASE CONTENTS - USERS TABLE")
            print("="*80)
            
            # Print column headers
            header = " | ".join(f"{col:>12}" for col in columns)
            print(header)
            print("-" * len(header))
            
            # Print user data
            for user in users:
                row = " | ".join(f"{str(val):>12}" for val in user)
                print(row)
                
            print("="*80)
            print(f"Total users: {len(users)}")
            conn.close()
        
    except Exception as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    view_users()