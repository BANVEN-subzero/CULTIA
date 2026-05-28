import os
import sys
from admin import app

if __name__ == '__main__':
    # Set the working directory to the project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create necessary directories
    os.makedirs('admin/static/css', exist_ok=True)
    os.makedirs('admin/static/js', exist_ok=True)
    os.makedirs('admin/static/images', exist_ok=True)
    os.makedirs('admin/templates/admin', exist_ok=True)
    os.makedirs('admin/uploads', exist_ok=True)
    os.makedirs('admin/backups', exist_ok=True)
    
    # Run the application on port 5001
    app.run(debug=True, port=5001)
