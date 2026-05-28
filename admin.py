from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort, send_from_directory
import os
import json
import uuid
import sqlite3
import threading
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin', 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin', 'static'))

# Configuration
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'ico'}
app.config['BACKUP_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')

# Ensure upload and backup directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['BACKUP_FOLDER'], exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_MAIN_DB_CANDIDATES = [
    os.path.join(BASE_DIR, 'Robix', 'Robix', 'backend', 'users.db'),
    os.path.join(BASE_DIR, 'Robix', 'Robix', 'users.db'),
]


def _resolve_main_app_db_path() -> str:
    for p in _MAIN_DB_CANDIDATES:
        if os.path.exists(p):
            return p
    # Default to the backend location (this is what the main app uses)
    return _MAIN_DB_CANDIDATES[0]


MAIN_APP_DB_PATH = _resolve_main_app_db_path()
main_db_lock = threading.Lock()


def _get_main_db_connection():
    conn = sqlite3.connect(MAIN_APP_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_main_db_schema():
    with main_db_lock:
        conn = _get_main_db_connection()
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                country TEXT,
                interest TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        existing_user_cols = {row['name'] for row in c.execute("PRAGMA table_info(users)").fetchall()}
        if 'country' not in existing_user_cols:
            c.execute("ALTER TABLE users ADD COLUMN country TEXT")
        if 'interest' not in existing_user_cols:
            c.execute("ALTER TABLE users ADD COLUMN interest TEXT")
        if 'created_at' not in existing_user_cols:
            c.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP")

        c.execute("UPDATE users SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP)")

        c.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_type TEXT NOT NULL,
                achievement_name TEXT NOT NULL,
                achievement_description TEXT,
                points INTEGER DEFAULT 0,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                progress_data TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                quiz_id TEXT,
                score INTEGER,
                total_questions INTEGER,
                percentage REAL,
                date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        conn.commit()
        conn.close()


def main_db_list_users(search: str, limit: int, offset: int):
    where = ''
    params = []
    if search:
        where = 'WHERE lower(first_name) LIKE ? OR lower(last_name) LIKE ? OR lower(email) LIKE ?'
        s = f"%{search.lower()}%"
        params.extend([s, s, s])

    with main_db_lock:
        conn = _get_main_db_connection()
        cur = conn.cursor()

        user_cols = {row['name'] for row in cur.execute("PRAGMA table_info(users)").fetchall()}
        has_created_at = 'created_at' in user_cols

        total = cur.execute(f'SELECT COUNT(1) as c FROM users {where}', params).fetchone()['c']

        if has_created_at:
            rows = cur.execute(
                f'''SELECT id, first_name, last_name, email, country, interest, created_at
                    FROM users
                    {where}
                    ORDER BY datetime(COALESCE(created_at, CURRENT_TIMESTAMP)) DESC, id DESC
                    LIMIT ? OFFSET ?''',
                params + [limit, offset],
            ).fetchall()
        else:
            rows = cur.execute(
                f'''SELECT id, first_name, last_name, email, country, interest, NULL as created_at
                    FROM users
                    {where}
                    ORDER BY id DESC
                    LIMIT ? OFFSET ?''',
                params + [limit, offset],
            ).fetchall()

        conn.close()

    return total, rows


def main_db_get_user(user_id: int):
    with main_db_lock:
        conn = _get_main_db_connection()
        row = conn.execute(
            'SELECT id, first_name, last_name, email, country, interest, created_at FROM users WHERE id = ?',
            (user_id,),
        ).fetchone()
        conn.close()
    return row


def main_db_insert_user(first_name: str, last_name: str, email: str, password: str, country: str, interest: str):
    with main_db_lock:
        conn = _get_main_db_connection()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO users (first_name, last_name, email, password, country, interest)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (first_name, last_name, email.lower(), generate_password_hash(password), country, interest),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
    return new_id


def main_db_update_user(user_id: int, first_name: str, last_name: str, email: str, country: str, interest: str, new_password: str | None):
    with main_db_lock:
        conn = _get_main_db_connection()
        cur = conn.cursor()
        if new_password:
            cur.execute(
                '''UPDATE users
                   SET first_name = ?, last_name = ?, email = ?, country = ?, interest = ?, password = ?
                   WHERE id = ?''',
                (first_name, last_name, email.lower(), country, interest, generate_password_hash(new_password), user_id),
            )
        else:
            cur.execute(
                '''UPDATE users
                   SET first_name = ?, last_name = ?, email = ?, country = ?, interest = ?
                   WHERE id = ?''',
                (first_name, last_name, email.lower(), country, interest, user_id),
            )
        conn.commit()
        conn.close()


def main_db_delete_user(user_id: int):
    with main_db_lock:
        conn = _get_main_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
        cur.execute('DELETE FROM achievements WHERE user_id = ?', (user_id,))
        cur.execute('DELETE FROM user_progress WHERE user_id = ?', (user_id,))
        cur.execute('DELETE FROM quiz_results WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()


def main_db_get_user_achievements(user_id: int):
    with main_db_lock:
        conn = _get_main_db_connection()
        cur = conn.cursor()
        rows = cur.execute(
            'SELECT id, achievement_type, achievement_name, achievement_description, points, earned_at FROM achievements WHERE user_id = ? ORDER BY earned_at DESC',
            (user_id,),
        ).fetchall()
        conn.close()
    return rows


def main_db_get_total_points(user_id: int):
    with main_db_lock:
        conn = _get_main_db_connection()
        cur = conn.cursor()
        row = cur.execute(
            'SELECT SUM(points) as total FROM achievements WHERE user_id = ?',
            (user_id,),
        ).fetchone()
        conn.close()
    return row['total'] if row and row['total'] else 0
    
def main_db_add_achievement(user_id: int, achievement_type: str, achievement_name: str, achievement_description: str, points: int):
    with main_db_lock:
        conn = _get_main_db_connection()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO achievements (user_id, achievement_type, achievement_name, achievement_description, points)
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, achievement_type, achievement_name, achievement_description, points)
        )
        conn.commit()
        conn.close()

def main_db_delete_achievement(achievement_id: int):
    with main_db_lock:
        conn = _get_main_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM achievements WHERE id = ?', (achievement_id,))
        conn.commit()
        conn.close()


def main_db_get_user_progress_summary(limit: int = 10):
    with main_db_lock:
        conn = _get_main_db_connection()
        cur = conn.cursor()

        # Ensure tables exist
        cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name IN ("user_progress","achievements")')
        tables = {row[0] for row in cur.fetchall()}

        out = []
        if 'user_progress' in tables:
            rows = cur.execute('''
                SELECT u.id, u.first_name, u.last_name, u.email,
                       COUNT(up.id) as progress_entries,
                       0 as achievements,
                       0 as total_points
                FROM users u
                LEFT JOIN user_progress up ON u.id = up.user_id
                GROUP BY u.id
                ORDER BY progress_entries DESC
                LIMIT ?
            ''', (limit,)).fetchall()
            out = [dict(r) for r in rows]
        conn.close()
    return out


def main_db_get_recent_achievements(limit: int = 10):
    with main_db_lock:
        conn = _get_main_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="achievements"')
        if cur.fetchone():
            rows = cur.execute('''
                SELECT a.achievement_name, a.points, a.earned_at,
                       u.first_name, u.last_name, u.email
                FROM achievements a
                JOIN users u ON a.user_id = u.id
                ORDER BY a.earned_at DESC
                LIMIT ?
            ''', (limit,)).fetchall()
            out = [dict(r) for r in rows]
        else:
            # Fallback: show recent user_progress entries as activity
            cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="user_progress"')
            if cur.fetchone():
                rows = cur.execute('''
                    SELECT up.feature_name as achievement_name, 0 as points, up.timestamp as earned_at,
                           u.first_name, u.last_name, u.email
                    FROM user_progress up
                    JOIN users u ON up.user_id = u.id
                    ORDER BY up.timestamp DESC
                    LIMIT ?
                ''', (limit,)).fetchall()
                out = [dict(r) for r in rows]
            else:
                out = []
        conn.close()
    return out

# Database models (in-memory for this example, replace with a real database in production)
class User:
    def __init__(self, id, username, password, email, is_active=True, is_admin=False, last_login=None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.is_active = is_active
        self.is_admin = is_admin
        self.last_login = last_login or datetime.utcnow()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# In-memory storage (replace with a database in production)
admin_users_db = {
    '1': User('1', 'admin', generate_password_hash('admin123'), 'admin@example.com', is_admin=True)
}

# Template context processor to make variables available in all templates
@app.context_processor
def inject_now():
    user = None
    user_id = session.get('user_id')
    if user_id:
        user = admin_users_db.get(str(user_id))

    return {
        'now': datetime.utcnow(),
        'app_name': 'CULTIA',
        'app_version': '1.0.0',
        'current_user': user,
    }



# Settings model
class Settings:
    def __init__(self):
        self.data = {
            'site_title': 'CULTIA Admin',
            'site_description': 'CULTIA administration panel',
            'site_url': 'http://localhost:5001',
            'admin_email': 'admin@example.com',
            'timezone': 'UTC',
            'date_format': 'Y-m-d',
            'time_format': 'H:i',
            'items_per_page': 10,
            'admin_theme': 'default',
            'primary_color': '#3498db',
            'logo_url': None,
            'favicon_url': None,
            'mail_driver': 'smtp',
            'smtp_host': 'smtp.example.com',
            'smtp_port': 587,
            'smtp_encryption': 'tls',
            'smtp_username': '',
            'smtp_password': '',
            'from_email': 'noreply@example.com',
            'from_name': 'Admin Panel',
            'allow_registration': False,
            'remember_me': True,
            'login_attempts': 5,
            'lockout_time': 30,
            'min_password_length': 8,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_number': True,
            'require_special_char': True,
            'password_expiry': 90,
            'enable_2fa': False,
            'two_factor_method': 'authenticator',
            'two_factor_required': False,
            'notify_new_user': True,
            'notify_failed_login': True,
            'notify_password_change': True,
            'in_app_updates': True,
            'in_app_messages': True,
            'debug_mode': False,
            'maintenance_mode': False,
            'cache_driver': 'simple',
            'session_driver': 'filesystem',
            'backup_enabled': False,
            'backup_frequency': 'daily',
            'backup_retention': 30
        }
        
        # Load settings from file if it exists
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
        self.load()
    
    def load(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    self.data.update(saved_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value
        self.save()
    
    def update_settings(self, new_settings):
        self.data.update(new_settings)
        return self.save()

# Initialize settings
app_settings = Settings()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        # Find user by username or email
        user = next((u for u in admin_users_db.values() if u.username == username or u.email == username), None)
        
        if user and check_password_hash(user.password, password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.', 'error')
                return render_template('admin/login.html', username=username)
                
            # Update last login
            user.last_login = datetime.utcnow()
            
            # Set session
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            # Set remember me
            if remember:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)
            
            flash('You have been successfully logged in!', 'success')
            
            # Redirect to intended page or dashboard
            next_page = request.args.get('next') or url_for('dashboard')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/logout')
def logout_alias():
    return logout()

@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
def dashboard():
    ensure_main_db_schema()

    with main_db_lock:
        conn = _get_main_db_connection()
        total_users = conn.execute('SELECT COUNT(1) as c FROM users').fetchone()['c']

        cols = {row['name'] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
        if 'created_at' in cols:
            recent_users = conn.execute(
                '''SELECT id, first_name, last_name, email, created_at
                   FROM users
                   ORDER BY datetime(COALESCE(created_at, CURRENT_TIMESTAMP)) DESC, id DESC
                   LIMIT 5'''
            ).fetchall()
        else:
            recent_users = conn.execute(
                '''SELECT id, first_name, last_name, email, NULL as created_at
                   FROM users
                   ORDER BY id DESC
                   LIMIT 5'''
            ).fetchall()
        conn.close()

    active_users = total_users

    # Fetch progress/achievements summaries for dashboard
    progress_summary = main_db_get_user_progress_summary(limit=5)
    recent_achievements = main_db_get_recent_achievements(limit=5)

    with main_db_lock:
        conn = _get_main_db_connection()
        cur = conn.cursor()
        
        # Get total quizzes taken
        cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="quiz_results"')
        if cur.fetchone():
            quizzes_taken = cur.execute('SELECT COUNT(1) as c FROM quiz_results').fetchone()['c']
        else:
            quizzes_taken = 0
            
        # Get total points earned by all users
        cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="achievements"')
        if cur.fetchone():
            total_points_earned = cur.execute('SELECT SUM(points) as s FROM achievements').fetchone()['s'] or 0
        else:
            total_points_earned = 0
            
        conn.close()

    stats = {
        'user_count': total_users,
        'active_sessions': active_users,
        'quizzes_taken': quizzes_taken,
        'total_points': total_points_earned,
        'new_users_today': 0,
        'pending_approvals': 0,
        'support_tickets': 0,
        'server_status': 'up',
    }

    recent_activities = [
        {
            'icon': 'fa-user',
            'text': 'Admin logged in',
            'time': (datetime.utcnow() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M')
        },
        {
            'icon': 'fa-cog',
            'text': 'Settings updated',
            'time': (datetime.utcnow() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
        },
    ]

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_users=recent_users,
        recent_activities=recent_activities,
        progress_summary=progress_summary,
        recent_achievements=recent_achievements,
    )

@app.route('/statistics')
@login_required
def statistics():
    return render_template('admin/dashboard.html', stats={}, recent_activities=[])

@app.route('/settings')
@login_required
def settings():
    if not session.get('is_admin'):
        abort(403)

    return render_template('admin/settings.html', settings=app_settings.data)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('admin/404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('admin/403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('admin/500.html'), 500

# File upload handling
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/admin/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin/debug/db')
@login_required
def debug_db():
    if not session.get('is_admin'):
        abort(403)

    ensure_main_db_schema()
    with main_db_lock:
        conn = _get_main_db_connection()
        cols = [row['name'] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
        conn.close()

    return jsonify({
        'db_path': MAIN_APP_DB_PATH,
        'users_columns': cols,
    })

# API Endpoints
@app.route('/admin/api/settings', methods=['POST'])
@login_required
def update_settings():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        if app_settings.update_settings(data):
            return jsonify({'success': True, 'message': 'Settings updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update settings'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# User management routes
@app.route('/admin/users')
@login_required
def users():
    if not session.get('is_admin'):
        abort(403)
    ensure_main_db_schema()

    search = (request.args.get('search') or '').strip()
    page = int(request.args.get('page') or 1)
    per_page = int(app_settings.data.get('items_per_page') or 10)
    if per_page < 1:
        per_page = 10
    if page < 1:
        page = 1

    total_users, user_list = main_db_list_users(search=search, limit=per_page, offset=(page - 1) * per_page)
    total_pages = max(1, (total_users + per_page - 1) // per_page)

    return render_template(
        'admin/users.html',
        users=user_list,
        search=search,
        total_users=total_users,
        page=page,
        total_pages=total_pages,
    )

@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not session.get('is_admin'):
        abort(403)

    ensure_main_db_schema()

    if request.method == 'POST':
        first_name = (request.form.get('first_name') or '').strip()
        last_name = (request.form.get('last_name') or '').strip()
        email = (request.form.get('email') or '').strip()
        password = request.form.get('password') or ''

        country = (request.form.get('country') or '').strip()
        interest = (request.form.get('interest') or '').strip()

        if not first_name or not last_name or not email or not password:
            flash('First name, last name, email, and password are required.', 'error')
            return render_template('admin/add_user.html', form=request.form)

        try:
            main_db_insert_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                country=country,
                interest=interest,
            )
        except sqlite3.IntegrityError:
            flash('That email is already registered.', 'error')
            return render_template('admin/add_user.html', form=request.form)

        flash('User created successfully.', 'success')
        return redirect(url_for('users'))

    return render_template('admin/add_user.html', form={})

@app.route('/users/<int:user_id>/achievements')
@login_required
def user_achievements(user_id):
    user = main_db_get_user(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('users'))
    
    achievements = main_db_get_user_achievements(user_id)
    total_points = main_db_get_total_points(user_id)
    
    return render_template('admin/user_achievements.html', 
                           user=user, 
                           achievements=achievements,
                           total_points=total_points)

@app.route('/users/<int:user_id>/achievements/add', methods=['POST'])
@login_required
def admin_add_achievement(user_id):
    if not session.get('is_admin'):
        abort(403)
    
    ensure_main_db_schema()
    
    ach_type = request.form.get('achievement_type', 'admin_granted')
    ach_name = request.form.get('achievement_name', 'Admin Bonus')
    ach_desc = request.form.get('achievement_description', 'Granted by an administrator')
    try:
        points = int(request.form.get('points', 0))
    except ValueError:
        points = 0
        
    main_db_add_achievement(int(user_id), ach_type, ach_name, ach_desc, points)
    flash(f'Successfully added {points} points and achievement.', 'success')
    return redirect(url_for('user_achievements', user_id=user_id))

@app.route('/admin/achievements/<int:achievement_id>/delete', methods=['POST'])
@login_required
def admin_delete_achievement(achievement_id):
    if not session.get('is_admin'):
        abort(403)
        
    ensure_main_db_schema()
    user_id = request.form.get('user_id')
    main_db_delete_achievement(achievement_id)
    flash('Achievement deleted successfully.', 'success')
    
    if user_id:
        return redirect(url_for('user_achievements', user_id=user_id))
    return redirect(url_for('users'))

@app.route('/admin/users/<user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not session.get('is_admin'):
        abort(403)

    ensure_main_db_schema()

    user = main_db_get_user(int(user_id))
    if not user:
        abort(404)

    if request.method == 'POST':
        first_name = (request.form.get('first_name') or '').strip()
        last_name = (request.form.get('last_name') or '').strip()
        email = (request.form.get('email') or '').strip()
        country = (request.form.get('country') or '').strip()
        interest = (request.form.get('interest') or '').strip()
        new_password = (request.form.get('password') or '').strip()

        if not first_name or not last_name or not email:
            flash('First name, last name, and email are required.', 'error')
            return render_template('admin/edit_user.html', user=user)

        try:
            main_db_update_user(
                user_id=int(user_id),
                first_name=first_name,
                last_name=last_name,
                email=email,
                country=country,
                interest=interest,
                new_password=new_password if new_password else None,
            )
        except sqlite3.IntegrityError:
            flash('That email is already registered.', 'error')
            return render_template('admin/edit_user.html', user=user)

        flash('User updated successfully.', 'success')
        return redirect(url_for('users'))

    return render_template('admin/edit_user.html', user=user)


@app.route('/admin/users/<user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not session.get('is_admin'):
        abort(403)

    ensure_main_db_schema()
    main_db_delete_user(int(user_id))
    flash('User deleted successfully.', 'success')
    return redirect(url_for('users'))

@app.route('/admin/users/<user_id>')
@login_required
def view_user(user_id):
    if not session.get('is_admin'):
        abort(403)

    ensure_main_db_schema()
    user = main_db_get_user(int(user_id))
    if not user:
        abort(404)

    return jsonify(dict(user))

# Backup and restore
@app.route('/admin/api/backup', methods=['POST'])
@login_required
def create_backup():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        # In a real app, this would create a database backup
        backup_id = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(app.config['BACKUP_FOLDER'], f'backup_{backup_id}.sql')
        
        # Simulate backup creation
        with open(backup_file, 'w') as f:
            f.write(f'-- Database backup created at {datetime.utcnow()}\n')
            f.write('-- This is a simulated backup. In a real app, this would contain your database dump.')
        
        return jsonify({
            'success': True, 
            'message': 'Backup created successfully',
            'filename': f'backup_{backup_id}.sql'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/api/backup/<filename>', methods=['DELETE'])
@login_required
def delete_backup(filename):
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        # Prevent directory traversal
        if '..' in filename or filename.startswith('/'):
            return jsonify({'success': False, 'message': 'Invalid filename'}), 400
        
        filepath = os.path.join(app.config['BACKUP_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'success': True, 'message': 'Backup deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Backup not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/api/backup/<filename>/download')
@login_required
def download_backup(filename):
    if not session.get('is_admin'):
        abort(403)
    
    # Prevent directory traversal
    if '..' in filename or filename.startswith('/'):
        abort(400)
    
    return send_from_directory(
        app.config['BACKUP_FOLDER'],
        filename,
        as_attachment=True,
        download_name=f'backup_{datetime.utcnow().strftime("%Y%m%d")}{os.path.splitext(filename)[1]}'
    )

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('admin/static/css', exist_ok=True)
    os.makedirs('admin/static/js', exist_ok=True)
    os.makedirs('admin/static/images', exist_ok=True)
    os.makedirs('admin/templates/admin', exist_ok=True)
    os.makedirs('admin/templates/admin/partials/settings', exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['BACKUP_FOLDER'], exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5001)
