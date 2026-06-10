import sqlite3
from flask import Blueprint, request, jsonify, session, redirect, url_for
import os
from werkzeug.security import generate_password_hash, check_password_hash
import threading

auth_bp = Blueprint('auth', __name__)
DB_PATH = os.path.join(os.environ.get('DATA_DIR', os.path.dirname(__file__)), 'users.db')

db_lock = threading.Lock()  # Thread lock to prevent database locking issues

def configure_sqlite():
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    cursor = conn.cursor()
    # Enable Write-Ahead Logging for better concurrency
    cursor.execute("PRAGMA journal_mode=WAL")
    # Set synchronous mode to NORMAL for better performance
    cursor.execute("PRAGMA synchronous=NORMAL")
    # Set cache size
    cursor.execute("PRAGMA cache_size=-64000")
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys=ON")
    conn.commit()
    conn.close()

def init_db():
    configure_sqlite()
    with db_lock:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        c = conn.cursor()
        
        # Users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                country TEXT,
                interest TEXT,
                profile_pic TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Migrations: Add missing columns if they don't exist
        c.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'role' not in columns:
            print("[DB] Migrating: Adding 'role' column to users table")
            c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
            
        if 'profile_pic' not in columns:
            print("[DB] Migrating: Adding 'profile_pic' column to users table")
            c.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT")
        
        if 'country' not in columns:
            c.execute("ALTER TABLE users ADD COLUMN country TEXT")
            
        if 'interest' not in columns:
            c.execute("ALTER TABLE users ADD COLUMN interest TEXT")
        
        # Achievements table
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
        
        # Persistent admin settings table
        c.execute('''
            CREATE TABLE IF NOT EXISTS admin_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                maintenance INTEGER DEFAULT 0,
                registrations INTEGER DEFAULT 1,
                ai INTEGER DEFAULT 1,
                storyteller INTEGER DEFAULT 1,
                verification INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            INSERT OR IGNORE INTO admin_settings (id, maintenance, registrations, ai, storyteller, verification)
            VALUES (1, 0, 1, 1, 1, 0)
        ''')
        
        # Persistent admin improvements log
        c.execute('''
            CREATE TABLE IF NOT EXISTS admin_improvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'Planned',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User progress table
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
        
        # Widgets configuration table
        c.execute('''
            CREATE TABLE IF NOT EXISTS widgets (
                widget_id TEXT PRIMARY KEY,
                widget_type TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                base_points INTEGER NOT NULL DEFAULT 10,
                difficulty_level INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Widget completions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS widget_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                widget_id TEXT NOT NULL,
                status TEXT NOT NULL,
                points_awarded INTEGER DEFAULT 0,
                points_deducted INTEGER DEFAULT 0,
                metadata TEXT,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (widget_id) REFERENCES widgets (widget_id)
            )
        ''')
        
        # Folklore stories table
        c.execute('''
            CREATE TABLE IF NOT EXISTS folklore_stories (
                story_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                tribe TEXT,
                content TEXT,
                word_count INTEGER,
                estimated_read_time_minutes INTEGER,
                base_points INTEGER DEFAULT 50,
                is_published INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Folklore progress table
        c.execute('''
            CREATE TABLE IF NOT EXISTS folklore_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                story_id TEXT NOT NULL,
                progress_percent INTEGER DEFAULT 0,
                last_read_position INTEGER DEFAULT 0,
                is_completed INTEGER DEFAULT 0,
                points_awarded INTEGER DEFAULT 0,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                UNIQUE(user_id, story_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (story_id) REFERENCES folklore_stories (story_id)
            )
        ''')
        
        # Gamification settings table
        c.execute('''
            CREATE TABLE IF NOT EXISTS gamification_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                penalty_percentage REAL DEFAULT 10.0,
                default_base_points INTEGER DEFAULT 10,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            INSERT OR IGNORE INTO gamification_settings (id, penalty_percentage, default_base_points)
            VALUES (1, 10.0, 10)
        ''')
        
        # Point transactions audit log
        c.execute('''
            CREATE TABLE IF NOT EXISTS point_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                reference_id TEXT,
                points_change INTEGER NOT NULL,
                description TEXT,
                admin_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (admin_id) REFERENCES users (id)
            )
        ''')
        
        # Seed initial widgets
        c.execute('''
            INSERT OR IGNORE INTO widgets (widget_id, widget_type, name, description, base_points, difficulty_level)
            VALUES 
            ('quiz_bamileke_1', 'quiz', 'Bamileke Kingdom Quiz', 'Test your knowledge about the Bamileke kingdom', 20, 2),
            ('quiz_bamun_1', 'quiz', 'Bamun Sultanate Quiz', 'Test your knowledge about the Bamun sultanate', 25, 3),
            ('lesson_fulani_herdsmen', 'lesson', 'Fulani Herdsmen Traditions', 'Learn about Fulani pastoral traditions', 15, 1),
            ('game_tribe_match', 'game', 'Tribe Matching Game', 'Match tribes to their regions', 30, 2)
        ''')
        
        # Seed initial folklore stories
        c.execute('''
            INSERT OR IGNORE INTO folklore_stories (story_id, title, tribe, base_points)
            VALUES 
            ('talking_python', 'The Talking Python', 'Bamileke', 50),
            ('magic_mirror', 'The Magic Mirror', 'Bamun', 50),
            ('woman_tree', 'The Sacred Tree Woman', 'Bamileke', 50),
            ('bird_fon', 'The Messenger Bird', 'Nsaw', 50),
            ('rainmaker_drum', 'The Rainmaker''s Drum', 'Bakossi', 50),
            ('river_goddess', 'The River Goddess', 'Bayangi', 50),
            ('crocodile_wouri', 'The Crocodile of Wouri', 'Duala', 50),
            ('forest_drummers', 'The Seven Drummers', 'Beti', 50),
            ('woman_snake', 'The Woman and the Snake', 'Fulani', 50),
            ('fire_sky', 'The Fire in the Sky', 'Northern', 50),
            ('wind_children', 'Children of the Wind', 'Sawa', 50),
            ('lobe_river', 'The Lobe River Secret', 'Batanga', 50),
            ('mountain_king', 'The Mountain King of Mount Cameroon', 'Bakweri', 50),
            ('hunter_pact', 'The Hunter''s Pact with the Forest', 'Bulu', 50),
            ('golden_fish', 'The Golden Fish of Lake Chad', 'Kotoko', 50),
            ('star_child', 'The Star Child of the Sky', 'Mafa', 50),
            ('first_cocoyam', 'The First Cocoyam', 'Widikum', 50),
            ('truth_mask', 'The Mask of Truth', 'Tikar', 50),
            ('leopard_chief', 'The Leopard and the Chief', 'Mbum', 50),
            ('spider_wisdom', 'The Wisdom of the Old Spider', 'Efik', 50),
            ('eternal_queen', 'The Queen Who Refused to Die', 'Bamiléké', 50),
            ('rain_bride', 'The Rain Bride of the Grassfields', 'Kom', 50),
            ('healing_leaves', 'The Healing Leaves of the Forest', 'Pygmy', 50),
            ('ancestor_wells', 'The Wells of the Ancestors', 'Mandara', 50)
        ''')
        
        conn.commit()
        conn.close()


@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() if request.is_json else request.form

    required = ['first_name', 'last_name', 'email', 'password', 'country', 'interest']
    if not all(k in data and data[k] for k in required):
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    hashed_pw = generate_password_hash(data['password'])
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('''
                INSERT INTO users (first_name, last_name, email, password, country, interest)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data['first_name'],
                data['last_name'],
                data['email'].lower(),
                hashed_pw,
                data['country'],
                data['interest']
            ))
            conn.commit()
            
            # Auto-login after registration
            c.execute('SELECT id, first_name, role FROM users WHERE email = ?', (data['email'].lower(),))
            user = c.fetchone()
            if user:
                session['user_id'] = user[0]
                session['first_name'] = user[1]
                session['role'] = user[2]
                
            conn.close()
        return jsonify({'success': True, 'message': 'Registration successful! Welcome to CULTIA.'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Email already registered.'}), 409
    except Exception as e:
        print(f"[ERROR] Registration failed: {e}")
        return jsonify({'success': False, 'message': f'Internal error: {str(e)}'}), 500


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() if request.is_json else request.form

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Missing email or password'}), 400

    with db_lock:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, password, first_name, role FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()

    if user:
        user_id, hashed_pw, first_name, role = user
        if check_password_hash(hashed_pw, password):
            # store session
            session['user_id'] = user_id
            session['first_name'] = first_name
            session['role'] = role
            return jsonify({
                'success': True, 
                'message': f'Welcome, {first_name}!',
                'user_id': user_id,
                'first_name': first_name,
                'role': role
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404


@auth_bp.route('/api/login-status', methods=['GET'])
def login_status():
    if 'user_id' in session:
        return jsonify({
            'success': True,
            'user_id': session['user_id'],
            'first_name': session['first_name'],
            'role': session.get('role', 'user')
        })
    return jsonify({'success': False, 'message': 'Not logged in'}), 401


@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


@auth_bp.route('/api/profile', methods=['GET'])
def get_profile():
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('SELECT first_name, last_name, email, country, interest, profile_pic FROM users WHERE id = ?', 
                      (session['user_id'],))
            user = c.fetchone()
            conn.close()

        if user:
            return jsonify({
                'success': True,
                'profile': {
                    'first_name': user[0],
                    'last_name': user[1],
                    'email': user[2],
                    'country': user[3],
                    'interest': user[4],
                    'profile_pic': user[5]
                }
            })
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500


@auth_bp.route('/api/profile', methods=['PUT'])
def update_profile():
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    data = request.get_json() if request.is_json else request.form

    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            
            # Update user profile
            c.execute('''
                UPDATE users 
                SET first_name = ?, last_name = ?, email = ?, country = ?, interest = ?
                WHERE id = ?
            ''', (
                data.get('first_name', ''),
                data.get('last_name', ''),
                data.get('email', '').lower(),
                data.get('country', ''),
                data.get('interest', ''),
                session['user_id']
            ))
            
            conn.commit()
            
            # Update session if name changed
            if data.get('first_name'):
                session['first_name'] = data.get('first_name')
                
            conn.close()
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating profile: {str(e)}'}), 500


@auth_bp.route('/api/achievements', methods=['GET'])
def get_achievements():
    """Get all achievements for the logged-in user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('''
                SELECT achievement_type, achievement_name, achievement_description, 
                       points, earned_at 
                FROM achievements 
                WHERE user_id = ? 
                ORDER BY earned_at DESC
            ''', (session['user_id'],))
            achievements = c.fetchall()
            conn.close()

        achievement_list = []
        for ach in achievements:
            achievement_list.append({
                'type': ach[0],
                'name': ach[1],
                'description': ach[2],
                'points': ach[3],
                'earned_at': ach[4]
            })

        return jsonify({
            'success': True,
            'achievements': achievement_list,
            'total_points': sum(a['points'] for a in achievement_list)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching achievements: {str(e)}'}), 500


@auth_bp.route('/api/achievements', methods=['POST'])
def add_achievement():
    """Add a new achievement for the logged-in user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    data = request.get_json()
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('''
                INSERT INTO achievements 
                (user_id, achievement_type, achievement_name, achievement_description, points)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session['user_id'],
                data.get('type', 'general'),
                data.get('name', ''),
                data.get('description', ''),
                data.get('points', 0)
            ))
            conn.commit()
            conn.close()

        return jsonify({'success': True, 'message': 'Achievement added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error adding achievement: {str(e)}'}), 500


@auth_bp.route('/api/progress', methods=['GET'])
def get_progress():
    """Get user progress data"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('''
                SELECT category, progress_data, last_updated 
                FROM user_progress 
                WHERE user_id = ?
            ''', (session['user_id'],))
            progress = c.fetchall()
            conn.close()

        progress_data = {}
        for p in progress:
            import json
            progress_data[p[0]] = {
                'data': json.loads(p[1]) if p[1] else {},
                'last_updated': p[2]
            }

        return jsonify({'success': True, 'progress': progress_data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching progress: {str(e)}'}), 500


@auth_bp.route('/api/progress', methods=['POST'])
def update_progress():
    """Update user progress data"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    data = request.get_json()
    category = data.get('category')
    progress_data = data.get('progress_data', {})
    
    try:
        import json
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            
            # Check if progress exists
            c.execute('SELECT id FROM user_progress WHERE user_id = ? AND category = ?', 
                     (session['user_id'], category))
            existing = c.fetchone()
            
            if existing:
                # Update existing
                c.execute('''
                    UPDATE user_progress 
                    SET progress_data = ?, last_updated = CURRENT_TIMESTAMP 
                    WHERE user_id = ? AND category = ?
                ''', (json.dumps(progress_data), session['user_id'], category))
            else:
                # Insert new
                c.execute('''
                    INSERT INTO user_progress (user_id, category, progress_data)
                    VALUES (?, ?, ?)
                ''', (session['user_id'], category, json.dumps(progress_data)))
            
            conn.commit()
            conn.close()

        return jsonify({'success': True, 'message': 'Progress updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating progress: {str(e)}'}), 500


@auth_bp.route('/api/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'success': False, 'message': 'Missing password fields'}), 400

    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('SELECT password FROM users WHERE id = ?', (session['user_id'],))
            user = c.fetchone()
            
            if user and check_password_hash(user[0], old_password):
                hashed_pw = generate_password_hash(new_password)
                c.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_pw, session['user_id']))
                conn.commit()
                conn.close()
                return jsonify({'success': True, 'message': 'Password changed successfully'})
            else:
                conn.close()
                return jsonify({'success': False, 'message': 'Invalid old password'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/api/delete-account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        user_id = session['user_id']
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            # Delete user and related data
            c.execute('DELETE FROM achievements WHERE user_id = ?', (user_id,))
            c.execute('DELETE FROM user_progress WHERE user_id = ?', (user_id,))
            c.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
        
        session.clear()
        return jsonify({'success': True, 'message': 'Account deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/api/profile/avatar', methods=['POST'])
def update_avatar():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.get_json()
    profile_pic = data.get('profile_pic')
    
    if not profile_pic:
        return jsonify({'success': False, 'message': 'No image data provided'}), 400
        
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('UPDATE users SET profile_pic = ? WHERE id = ?', (profile_pic, session['user_id']))
            conn.commit()
            conn.close()
        return jsonify({'success': True, 'message': 'Avatar updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('''
                SELECT id, first_name, last_name, email, role, country, created_at 
                FROM users 
                ORDER BY created_at DESC
            ''')
            users = c.fetchall()
            conn.close()

        user_list = []
        for u in users:
            user_list.append({
                'id': u[0],
                'first_name': u[1],
                'last_name': u[2],
                'email': u[3],
                'role': u[4],
                'country': u[5],
                'created_at': u[6]
            })

        return jsonify({'success': True, 'users': user_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/api/admin/user/<int:user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            # Delete user and related data
            c.execute('DELETE FROM achievements WHERE user_id = ?', (user_id,))
            c.execute('DELETE FROM user_progress WHERE user_id = ?', (user_id,))
            c.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
        return jsonify({'success': True, 'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/api/admin/user/role', methods=['POST'])
def admin_update_role():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    user_id = data.get('user_id')
    new_role = data.get('role')

    if not user_id or not new_role:
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
            conn.commit()
            conn.close()
        return jsonify({'success': True, 'message': 'User role updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/api/admin/stats', methods=['GET'])
def admin_get_stats():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            
            # Total users
            c.execute('SELECT COUNT(*) FROM users')
            total_users = c.fetchone()[0]
            
            # Total achievements
            c.execute('SELECT COUNT(*) FROM achievements')
            total_achievements = c.fetchone()[0]
            
            # Total points awarded
            c.execute('SELECT SUM(points) FROM achievements')
            total_points = c.fetchone()[0] or 0
            
            # Users by country
            c.execute('SELECT country, COUNT(*) FROM users GROUP BY country ORDER BY COUNT(*) DESC LIMIT 5')
            countries = c.fetchall()
            
            conn.close()

        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_achievements': total_achievements,
                'total_points': total_points,
                'countries': [{'country': c[0], 'count': c[1]} for c in countries]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get the leaderboard data"""
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            
            # Aggregate points per user from achievements table
            # Only show users with at least 0 points, order by points then name
            c.execute('''
                SELECT u.id, u.first_name, u.last_name, COALESCE(SUM(a.points), 0) as total_points
                FROM users u
                LEFT JOIN achievements a ON u.id = a.user_id
                GROUP BY u.id
                ORDER BY total_points DESC, u.first_name ASC, u.last_name ASC
                LIMIT 10
            ''')
            results = c.fetchall()
            conn.close()
            
        leaderboard = []
        current_user_id = session.get('user_id')
        for index, row in enumerate(results):
            user_id = row[0]
            first_name = row[1] or ''
            last_name = row[2] or ''
            points = row[3] if row[3] else 0
            full_name = f"{first_name} {last_name}".strip() or 'Anonymous'

            leaderboard.append({
                'rank': index + 1,
                'name': full_name,
                'points': points,
                'is_current_user': user_id == current_user_id
            })
            
        return jsonify({'success': True, 'leaderboard': leaderboard})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching leaderboard: {str(e)}'}), 500


# ==================== GAMIFICATION ENDPOINTS ====================

@auth_bp.route('/api/widgets', methods=['GET'])
def get_widgets():
    """Get all active widgets"""
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('''
                SELECT widget_id, widget_type, name, description, base_points, difficulty_level
                FROM widgets WHERE is_active = 1
            ''')
            widgets = c.fetchall()
            conn.close()
        
        widget_list = []
        for w in widgets:
            widget_list.append({
                'widget_id': w[0],
                'widget_type': w[1],
                'name': w[2],
                'description': w[3],
                'base_points': w[4],
                'difficulty_level': w[5]
            })
        
        return jsonify({'success': True, 'widgets': widget_list})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching widgets: {str(e)}'}), 500


@auth_bp.route('/api/widgets/<widget_id>/complete', methods=['POST'])
def complete_widget(widget_id):
    """Record widget completion and award points"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            
            # Get widget base points
            c.execute('SELECT base_points FROM widgets WHERE widget_id = ?', (widget_id,))
            widget = c.fetchone()
            if not widget:
                return jsonify({'success': False, 'message': 'Widget not found'}), 404
            base_points = widget[0]
            
            # Check if already completed
            c.execute('''
                SELECT 1 FROM widget_completions 
                WHERE user_id = ? AND widget_id = ? AND status = 'completed'
            ''', (user_id, widget_id))
            if c.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': 'Widget already completed', 'points_awarded': 0})
            
            # Record completion
            c.execute('''
                INSERT INTO widget_completions 
                (user_id, widget_id, status, points_awarded)
                VALUES (?, ?, 'completed', ?)
            ''', (user_id, widget_id, base_points))
            
            # Add achievement
            c.execute('''
                INSERT INTO achievements 
                (user_id, achievement_type, achievement_name, achievement_description, points)
                VALUES (?, 'widget_points', ?, 'Completed widget successfully', ?)
            ''', (user_id, f"Widget: {widget_id}", base_points))
            
            # Record transaction
            c.execute('''
                INSERT INTO point_transactions 
                (user_id, transaction_type, reference_id, points_change, description)
                VALUES (?, 'widget_complete', ?, ?, ?)
            ''', (user_id, widget_id, base_points, f"Completed widget: {widget_id}"))
            
            conn.commit()
            conn.close()
        
        return jsonify({'success': True, 'points_awarded': base_points})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/api/widgets/<widget_id>/fail', methods=['POST'])
def fail_widget(widget_id):
    """Record widget failure and apply penalty"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            
            # Get settings and widget base points
            c.execute('SELECT penalty_percentage FROM gamification_settings WHERE id = 1')
            settings = c.fetchone()
            penalty_pct = settings[0] if settings else 10.0
            
            c.execute('SELECT base_points FROM widgets WHERE widget_id = ?', (widget_id,))
            widget = c.fetchone()
            if not widget:
                return jsonify({'success': False, 'message': 'Widget not found'}), 404
            base_points = widget[0]
            
            penalty = int(base_points * (penalty_pct / 100.0))
            
            # Record failure
            c.execute('''
                INSERT INTO widget_completions 
                (user_id, widget_id, status, points_deducted)
                VALUES (?, ?, 'failed', ?)
            ''', (user_id, widget_id, penalty))
            
            # Add achievement (negative points)
            c.execute('''
                INSERT INTO achievements 
                (user_id, achievement_type, achievement_name, achievement_description, points)
                VALUES (?, 'widget_penalty', ?, 'Failed widget penalty', ?)
            ''', (user_id, f"Widget: {widget_id}", -penalty))
            
            # Record transaction
            c.execute('''
                INSERT INTO point_transactions 
                (user_id, transaction_type, reference_id, points_change, description)
                VALUES (?, 'widget_fail', ?, ?, ?)
            ''', (user_id, widget_id, -penalty, f"Failed widget: {widget_id} (-{penalty} penalty)"))
            
            conn.commit()
            conn.close()
        
        return jsonify({'success': True, 'points_deducted': penalty})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/api/folklore/stories', methods=['GET'])
def get_folklore_stories():
    """Get all published folklore stories"""
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('''
                SELECT story_id, title, tribe, content, word_count, 
                       estimated_read_time_minutes, base_points 
                FROM folklore_stories WHERE is_published = 1
            ''')
            stories = c.fetchall()
            conn.close()
        
        story_list = []
        for s in stories:
            story_list.append({
                'story_id': s[0],
                'title': s[1],
                'tribe': s[2],
                'content': s[3],
                'word_count': s[4],
                'estimated_read_time_minutes': s[5],
                'base_points': s[6]
            })
        
        return jsonify({'success': True, 'stories': story_list})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching stories: {str(e)}'}), 500


@auth_bp.route('/api/folklore/progress', methods=['GET'])
def get_folklore_progress():
    """Get user's folklore progress"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('''
                SELECT story_id, progress_percent, is_completed, points_awarded, started_at, completed_at
                FROM folklore_progress WHERE user_id = ?
            ''', (user_id,))
            progress = c.fetchall()
            conn.close()
        
        progress_list = {}
        for p in progress:
            progress_list[p[0]] = {
                'progress_percent': p[1],
                'is_completed': bool(p[2]),
                'points_awarded': p[3],
                'started_at': p[4],
                'completed_at': p[5]
            }
        
        return jsonify({'success': True, 'progress': progress_list})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching progress: {str(e)}'}), 500


@auth_bp.route('/api/folklore/progress/<story_id>', methods=['POST'])
def update_folklore_progress(story_id):
    """Update folklore reading progress (no points)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    user_id = session['user_id']
    data = request.get_json()
    progress_percent = data.get('progress_percent', 0)
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            
            # Check existing
            c.execute('''
                SELECT id FROM folklore_progress WHERE user_id = ? AND story_id = ?
            ''', (user_id, story_id))
            existing = c.fetchone()
            
            if existing:
                c.execute('''
                    UPDATE folklore_progress 
                    SET progress_percent = ?
                    WHERE user_id = ? AND story_id = ?
                ''', (progress_percent, user_id, story_id))
            else:
                c.execute('''
                    INSERT INTO folklore_progress (user_id, story_id, progress_percent)
                    VALUES (?, ?, ?)
                ''', (user_id, story_id, progress_percent))
            
            conn.commit()
            conn.close()
        
        return jsonify({'success': True, 'message': 'Progress updated'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/api/folklore/progress/<story_id>/complete', methods=['POST'])
def complete_folklore_story(story_id):
    """Mark folklore story as completed and award points"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            
            # Get story base points
            c.execute('SELECT base_points FROM folklore_stories WHERE story_id = ?', (story_id,))
            story = c.fetchone()
            if not story:
                return jsonify({'success': False, 'message': 'Story not found'}), 404
            base_points = story[0]
            
            # Check existing progress
            c.execute('''
                SELECT is_completed, points_awarded FROM folklore_progress 
                WHERE user_id = ? AND story_id = ?
            ''', (user_id, story_id))
            existing = c.fetchone()
            
            if existing and existing[0] == 1:
                conn.close()
                return jsonify({'success': False, 'message': 'Story already completed', 'points_awarded': 0})
            
            # Update or insert progress
            if existing:
                c.execute('''
                    UPDATE folklore_progress 
                    SET progress_percent = 100, is_completed = 1, points_awarded = ?, completed_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND story_id = ?
                ''', (base_points, user_id, story_id))
            else:
                c.execute('''
                    INSERT INTO folklore_progress 
                    (user_id, story_id, progress_percent, is_completed, points_awarded, completed_at)
                    VALUES (?, ?, 100, 1, ?, CURRENT_TIMESTAMP)
                ''', (user_id, story_id, base_points))
            
            # Add achievement
            c.execute('''
                INSERT INTO achievements 
                (user_id, achievement_type, achievement_name, achievement_description, points)
                VALUES (?, 'folklore_points', ?, 'Completed folklore story', ?)
            ''', (user_id, f"Story: {story_id}", base_points))
            
            # Record transaction
            c.execute('''
                INSERT INTO point_transactions 
                (user_id, transaction_type, reference_id, points_change, description)
                VALUES (?, 'folklore_complete', ?, ?, ?)
            ''', (user_id, story_id, base_points, f"Completed folklore story: {story_id}"))
            
            conn.commit()
            conn.close()
        
        return jsonify({'success': True, 'points_awarded': base_points})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/api/dashboard/folklore-points', methods=['GET'])
def get_dashboard_folklore_points():
    """Get folklore points to earn for dashboard"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('''
                SELECT 
                    s.story_id,
                    s.title,
                    s.tribe,
                    s.base_points,
                    COALESCE(fp.progress_percent, 0) as current_progress,
                    COALESCE(fp.is_completed, 0) as is_completed
                FROM folklore_stories s
                LEFT JOIN folklore_progress fp ON s.story_id = fp.story_id AND fp.user_id = ?
                WHERE s.is_published = 1
                ORDER BY s.base_points DESC
            ''', (user_id,))
            stories = c.fetchall()
            conn.close()
        
        story_list = []
        for s in stories:
            story_list.append({
                'story_id': s[0],
                'title': s[1],
                'tribe': s[2],
                'base_points': s[3],
                'current_progress': s[4],
                'is_completed': bool(s[5])
            })
        
        return jsonify({'success': True, 'stories': story_list})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/api/folklore/completed-count', methods=['GET'])
def get_completed_stories_count():
    """Get number of completed folklore stories for current user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    user_id = session['user_id']
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('''
                SELECT COUNT(*) FROM folklore_progress 
                WHERE user_id = ? AND is_completed = 1
            ''', (user_id,))
            count = c.fetchone()[0]
            conn.close()
        
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== ADMIN GAMIFICATION ENDPOINTS ====================

@auth_bp.route('/api/admin/gamification/settings', methods=['GET'])
def get_gamification_settings():
    """Get gamification settings (admin only)"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('SELECT penalty_percentage, default_base_points FROM gamification_settings WHERE id = 1')
            settings = c.fetchone()
            conn.close()
        
        if settings:
            return jsonify({
                'success': True,
                'settings': {
                    'penalty_percentage': settings[0],
                    'default_base_points': settings[1]
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Settings not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/api/admin/gamification/settings', methods=['PUT'])
def update_gamification_settings():
    """Update gamification settings (admin only)"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('''
                UPDATE gamification_settings 
                SET penalty_percentage = ?, default_base_points = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
            ''', (data.get('penalty_percentage', 10.0), data.get('default_base_points', 10)))
            conn.commit()
            conn.close()
        
        return jsonify({'success': True, 'message': 'Settings updated'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/api/admin/gamification/transactions', methods=['GET'])
def get_point_transactions():
    """Get all point transactions for audit (admin only)"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            c = conn.cursor()
            c.execute('''
                SELECT pt.id, u.first_name, u.last_name, pt.transaction_type, 
                       pt.reference_id, pt.points_change, pt.description, pt.created_at
                FROM point_transactions pt
                JOIN users u ON pt.user_id = u.id
                ORDER BY pt.created_at DESC
                LIMIT 100
            ''')
            transactions = c.fetchall()
            conn.close()
        
        tx_list = []
        for tx in transactions:
            tx_list.append({
                'id': tx[0],
                'user_name': f"{tx[1]} {tx[2]}",
                'transaction_type': tx[3],
                'reference_id': tx[4],
                'points_change': tx[5],
                'description': tx[6],
                'created_at': tx[7]
            })
        
        return jsonify({'success': True, 'transactions': tx_list})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500