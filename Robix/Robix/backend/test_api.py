
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Trying to import api.py...")
try:
    import api
    print("Successfully imported api.py! Now checking for app...")
    if hasattr(api, 'app'):
        print("App found! Now trying to run...")
        api.init_db()
        api.app.run(host='0.0.0.0', port=5000, debug=True)
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    print(traceback.format_exc())
