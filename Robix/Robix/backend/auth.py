import sqlite3
from flask import Blueprint, request, jsonify, session, redirect, url_for
import os
from werkzeug.security import generate_password_hash, check_password_hash
import threading

auth_bp = Blueprint('auth', __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

db_lock = threading.Lock()  # Thread lock to prevent database locking issues


def init_db():
    with db_lock:
        conn = sqlite3.connect(DB_PATH)
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
            conn = sqlite3.connect(DB_PATH)
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
            # 🔑 store session
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
            conn = sqlite3.connect(DB_PATH)
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
            conn = sqlite3.connect(DB_PATH)
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
            conn = sqlite3.connect(DB_PATH)
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
            conn = sqlite3.connect(DB_PATH)
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
            conn = sqlite3.connect(DB_PATH)
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
            conn = sqlite3.connect(DB_PATH)
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
            conn = sqlite3.connect(DB_PATH)
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
            conn = sqlite3.connect(DB_PATH)
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
            conn = sqlite3.connect(DB_PATH)
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
            conn = sqlite3.connect(DB_PATH)
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
            conn = sqlite3.connect(DB_PATH)
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
            conn = sqlite3.connect(DB_PATH)
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
            conn = sqlite3.connect(DB_PATH)
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
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Aggregate points per user from achievements table
            # Only show users with at least 0 points, order by points then name
            c.execute('''
                SELECT u.first_name, COALESCE(SUM(a.points), 0) as total_points
                FROM users u
                LEFT JOIN achievements a ON u.id = a.user_id
                GROUP BY u.id
                ORDER BY total_points DESC, u.first_name ASC
                LIMIT 10
            ''')
            results = c.fetchall()
            conn.close()
            
        leaderboard = []
        for index, row in enumerate(results):
            name = row[0] if row[0] else 'Anonymous'
            points = row[1] if row[1] else 0
            
            is_current_user = False
            if 'first_name' in session and name == session['first_name']:
                is_current_user = True

            leaderboard.append({
                'rank': index + 1,
                'name': name,
                'points': points,
                'is_current_user': is_current_user
            })
            
        return jsonify({'success': True, 'leaderboard': leaderboard})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching leaderboard: {str(e)}'}), 500