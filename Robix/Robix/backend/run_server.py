
import sys
import os

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Current directory:", os.getcwd())
print("Python path:", sys.path)

# Redirect stdout and stderr to a log file
log_file = open("server_log.txt", "w", encoding="utf-8")
sys.stdout = log_file
sys.stderr = log_file

print("=== Starting server ===")

try:
    from api import app, init_db
    init_db()
    print("Database initialized")
    
    print("Starting Flask app on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
except Exception as e:
    print("ERROR starting server:", type(e), str(e))
    import traceback
    print(traceback.format_exc())
    log_file.close()
    sys.exit(1)
