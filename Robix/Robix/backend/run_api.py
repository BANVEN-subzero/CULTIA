
import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import app, init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Starting CULTIA server at http://localhost:5000...")
    app.run(host='localhost', port=5000, debug=False, use_reloader=False)

