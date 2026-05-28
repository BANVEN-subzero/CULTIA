import sqlite3
import os
import threading

db_lock = threading.Lock()  # Thread lock to prevent database locking issues

# Connect to the database
db_path = os.path.join(os.path.dirname(__file__), 'users.db')

with db_lock:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query all users
    cursor.execute("SELECT id, first_name, last_name, email, country, interest FROM users")
    users = cursor.fetchall()
    
    print("Registered Users:")
    print("-" * 80)
    print(f"{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Email':<25} {'Country':<15} {'Interest':<15}")
    print("-" * 80)
    
    for user in users:
        print(f"{user[0]:<5} {user[1]:<15} {user[2]:<15} {user[3]:<25} {user[4]:<15} {user[5]:<15}")
    
    # Close the connection
    conn.close()