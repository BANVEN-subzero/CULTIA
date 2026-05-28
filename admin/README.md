# Admin Panel for Robix1

A comprehensive admin panel built with Flask for managing the Robix1 application.

## Features

- User authentication (login/logout)
- Dashboard with statistics and recent activity
- User management (view, add, edit, delete users)
- System settings management
- Backup and restore functionality
- Responsive design

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Robix1
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root with the following variables:
   ```
   FLASK_APP=admin.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   ```

## Running the Application

1. Start the development server:
   ```bash
   flask run
   ```
   or
   ```bash
   python admin.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000/admin
   ```

3. Login with the default admin credentials:
   - Username: admin
   - Password: admin123

## Project Structure

```
admin/
├── static/               # Static files (CSS, JS, images)
│   ├── css/             # Stylesheets
│   └── js/              # JavaScript files
├── templates/           # HTML templates
│   └── admin/           # Admin panel templates
│       ├── partials/    # Reusable template components
│       ├── base.html    # Base template
│       ├── dashboard.html
│       ├── login.html
│       └── users.html
├── uploads/             # User uploaded files
├── backups/             # Database backups
├── admin.py             # Main application file
└── settings.json        # Application settings
```

## Security Considerations

- Change the default admin password after first login
- Use a strong secret key in production
- Enable HTTPS in production
- Keep dependencies up to date
- Regularly back up your data

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
