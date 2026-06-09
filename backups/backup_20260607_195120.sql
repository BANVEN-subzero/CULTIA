-- CULTIA Database Backup
-- Created: 2026-06-07T19:51:20.126240
-- DB Path: C:\Users\BANVEN\Desktop\CULTIA main\CULTIA\Robix\Robix\backend\users.db

-- Table: achievements
CREATE TABLE achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_type TEXT NOT NULL,
                achievement_name TEXT NOT NULL,
                achievement_description TEXT,
                points INTEGER DEFAULT 0,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (1, 1, 'points', 'Points Earned', 'Activity: quiz', 90, '2026-06-01 10:42:15');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (2, 1, 'first_quiz', 'Quiz Starter', 'Completed your first language quiz', 50, '2026-06-01 10:42:16');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (3, 1, 'first_quiz', 'Quiz Starter', 'Completed your first language quiz', 50, '2026-06-01 10:42:16');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (4, 1, 'points', 'Points Earned', 'Activity: lesson', 10, '2026-06-01 10:45:59');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (5, 1, 'first_lesson', 'First Steps', 'Completed your first language lesson', 50, '2026-06-01 10:45:59');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (6, 1, 'first_lesson', 'First Steps', 'Completed your first language lesson', 50, '2026-06-01 10:45:59');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (7, 1, 'first_lesson', 'First Steps', 'Completed your first language lesson', 50, '2026-06-01 10:46:00');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (8, 1, 'points', 'Points Earned', 'Activity: quiz', 50, '2026-06-01 10:47:40');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (9, 1, 'points', 'Points Earned', 'Activity: quiz', 20, '2026-06-01 10:47:40');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (10, 2, 'points', 'Points Earned', 'Activity: quiz', 100, '2026-06-01 11:17:55');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (11, 2, 'first_quiz', 'Quiz Starter', 'Completed your first language quiz', 50, '2026-06-01 11:17:55');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (12, 2, 'first_quiz', 'Quiz Starter', 'Completed your first language quiz', 50, '2026-06-01 11:17:55');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (13, 2, 'folklore_points', 'Story: talking_python', 'Completed folklore story', 50, '2026-06-02 03:26:46');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (14, 2, 'folklore_points', 'Story: magic_mirror', 'Completed folklore story', 50, '2026-06-02 04:02:51');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (15, 2, 'folklore_points', 'Story: woman_tree', 'Completed folklore story', 50, '2026-06-02 04:04:21');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (16, 3, 'folklore_points', 'Story: bird_fon', 'Completed folklore story', 50, '2026-06-02 04:33:16');
INSERT INTO achievements (id, user_id, achievement_type, achievement_name, achievement_description, points, earned_at) VALUES (17, 3, 'folklore_points', 'Story: woman_tree', 'Completed folklore story', 50, '2026-06-07 01:56:47');

-- Table: admin_improvements
CREATE TABLE admin_improvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'Planned',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );


-- Table: admin_settings
CREATE TABLE admin_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                maintenance INTEGER DEFAULT 0,
                registrations INTEGER DEFAULT 1,
                ai INTEGER DEFAULT 1,
                storyteller INTEGER DEFAULT 1,
                verification INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

INSERT INTO admin_settings (id, maintenance, registrations, ai, storyteller, verification, updated_at) VALUES (1, 0, 1, 1, 1, 0, '2026-06-01 10:34:25');

-- Table: folklore_progress
CREATE TABLE folklore_progress (
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
            );

INSERT INTO folklore_progress (id, user_id, story_id, progress_percent, last_read_position, is_completed, points_awarded, started_at, completed_at) VALUES (1, 2, 'talking_python', 100, 0, 1, 50, '2026-06-02 03:26:46', '2026-06-02 03:26:46');
INSERT INTO folklore_progress (id, user_id, story_id, progress_percent, last_read_position, is_completed, points_awarded, started_at, completed_at) VALUES (2, 2, 'magic_mirror', 100, 0, 1, 50, '2026-06-02 04:02:51', '2026-06-02 04:02:51');
INSERT INTO folklore_progress (id, user_id, story_id, progress_percent, last_read_position, is_completed, points_awarded, started_at, completed_at) VALUES (3, 2, 'woman_tree', 100, 0, 1, 50, '2026-06-02 04:04:21', '2026-06-02 04:04:21');
INSERT INTO folklore_progress (id, user_id, story_id, progress_percent, last_read_position, is_completed, points_awarded, started_at, completed_at) VALUES (4, 3, 'bird_fon', 100, 0, 1, 50, '2026-06-02 04:33:16', '2026-06-02 04:33:16');
INSERT INTO folklore_progress (id, user_id, story_id, progress_percent, last_read_position, is_completed, points_awarded, started_at, completed_at) VALUES (5, 3, 'woman_tree', 100, 0, 1, 50, '2026-06-07 01:56:47', '2026-06-07 01:56:47');

-- Table: folklore_stories
CREATE TABLE folklore_stories (
                story_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                tribe TEXT,
                content TEXT,
                word_count INTEGER,
                estimated_read_time_minutes INTEGER,
                base_points INTEGER DEFAULT 50,
                is_published INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

INSERT INTO folklore_stories (story_id, title, tribe, content, word_count, estimated_read_time_minutes, base_points, is_published, created_at) VALUES ('talking_python', 'The Talking Python', 'Bamileke', NULL, NULL, NULL, 50, 1, '2026-06-02 03:19:19');
INSERT INTO folklore_stories (story_id, title, tribe, content, word_count, estimated_read_time_minutes, base_points, is_published, created_at) VALUES ('magic_mirror', 'The Magic Mirror', 'Bamun', NULL, NULL, NULL, 50, 1, '2026-06-02 03:19:19');
INSERT INTO folklore_stories (story_id, title, tribe, content, word_count, estimated_read_time_minutes, base_points, is_published, created_at) VALUES ('woman_tree', 'The Sacred Tree Woman', 'Bamileke', NULL, NULL, NULL, 50, 1, '2026-06-02 03:19:19');
INSERT INTO folklore_stories (story_id, title, tribe, content, word_count, estimated_read_time_minutes, base_points, is_published, created_at) VALUES ('bird_fon', 'The Messenger Bird', 'Nsaw', NULL, NULL, NULL, 50, 1, '2026-06-02 03:19:19');
INSERT INTO folklore_stories (story_id, title, tribe, content, word_count, estimated_read_time_minutes, base_points, is_published, created_at) VALUES ('rainmaker_drum', 'The Rainmaker''s Drum', 'Bakossi', NULL, NULL, NULL, 50, 1, '2026-06-02 03:19:19');
INSERT INTO folklore_stories (story_id, title, tribe, content, word_count, estimated_read_time_minutes, base_points, is_published, created_at) VALUES ('river_goddess', 'The River Goddess', 'Bayangi', NULL, NULL, NULL, 50, 1, '2026-06-02 03:19:19');
INSERT INTO folklore_stories (story_id, title, tribe, content, word_count, estimated_read_time_minutes, base_points, is_published, created_at) VALUES ('crocodile_wouri', 'The Crocodile of Wouri', 'Duala', NULL, NULL, NULL, 50, 1, '2026-06-02 03:19:19');
INSERT INTO folklore_stories (story_id, title, tribe, content, word_count, estimated_read_time_minutes, base_points, is_published, created_at) VALUES ('forest_drummers', 'The Seven Drummers', 'Beti', NULL, NULL, NULL, 50, 1, '2026-06-02 03:19:19');
INSERT INTO folklore_stories (story_id, title, tribe, content, word_count, estimated_read_time_minutes, base_points, is_published, created_at) VALUES ('woman_snake', 'The Woman and the Snake', 'Fulani', NULL, NULL, NULL, 50, 1, '2026-06-02 03:19:19');
INSERT INTO folklore_stories (story_id, title, tribe, content, word_count, estimated_read_time_minutes, base_points, is_published, created_at) VALUES ('fire_sky', 'The Fire in the Sky', 'Northern', NULL, NULL, NULL, 50, 1, '2026-06-02 03:19:19');
INSERT INTO folklore_stories (story_id, title, tribe, content, word_count, estimated_read_time_minutes, base_points, is_published, created_at) VALUES ('wind_children', 'Children of the Wind', 'Sawa', NULL, NULL, NULL, 50, 1, '2026-06-02 03:19:19');
INSERT INTO folklore_stories (story_id, title, tribe, content, word_count, estimated_read_time_minutes, base_points, is_published, created_at) VALUES ('lobe_river', 'The Lobe River Secret', 'Batanga', NULL, NULL, NULL, 50, 1, '2026-06-02 03:19:19');

-- Table: gamification_settings
CREATE TABLE gamification_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                penalty_percentage REAL DEFAULT 10.0,
                default_base_points INTEGER DEFAULT 10,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

INSERT INTO gamification_settings (id, penalty_percentage, default_base_points, updated_at) VALUES (1, 10.0, 10, '2026-06-02 03:19:19');

-- Table: point_transactions
CREATE TABLE point_transactions (
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
            );

INSERT INTO point_transactions (id, user_id, transaction_type, reference_id, points_change, description, admin_id, created_at) VALUES (1, 2, 'folklore_completed', 'talking_python', 50, 'Completed story: talking_python', NULL, '2026-06-02 03:26:46');
INSERT INTO point_transactions (id, user_id, transaction_type, reference_id, points_change, description, admin_id, created_at) VALUES (2, 2, 'folklore_complete', 'magic_mirror', 50, 'Completed folklore story: magic_mirror', NULL, '2026-06-02 04:02:51');
INSERT INTO point_transactions (id, user_id, transaction_type, reference_id, points_change, description, admin_id, created_at) VALUES (3, 2, 'folklore_complete', 'woman_tree', 50, 'Completed folklore story: woman_tree', NULL, '2026-06-02 04:04:21');
INSERT INTO point_transactions (id, user_id, transaction_type, reference_id, points_change, description, admin_id, created_at) VALUES (4, 3, 'folklore_complete', 'bird_fon', 50, 'Completed folklore story: bird_fon', NULL, '2026-06-02 04:33:16');
INSERT INTO point_transactions (id, user_id, transaction_type, reference_id, points_change, description, admin_id, created_at) VALUES (5, 3, 'folklore_complete', 'woman_tree', 50, 'Completed folklore story: woman_tree', NULL, '2026-06-07 01:56:47');

-- Table: quiz_results
CREATE TABLE quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                quiz_id TEXT,
                score INTEGER,
                total_questions INTEGER,
                percentage REAL,
                date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

INSERT INTO quiz_results (id, user_id, quiz_id, score, total_questions, percentage, date_taken) VALUES (1, 1, 'cameroon-geography', 9, 10, 90.0, '2026-06-01 10:42:15');
INSERT INTO quiz_results (id, user_id, quiz_id, score, total_questions, percentage, date_taken) VALUES (2, 2, 'cameroon-history', 10, 10, 100.0, '2026-06-01 11:17:55');

-- Table: sqlite_sequence
CREATE TABLE sqlite_sequence(name,seq);

INSERT INTO sqlite_sequence (name, seq) VALUES ('users', 4);
INSERT INTO sqlite_sequence (name, seq) VALUES ('user_progress', 3);
INSERT INTO sqlite_sequence (name, seq) VALUES ('achievements', 17);
INSERT INTO sqlite_sequence (name, seq) VALUES ('quiz_results', 2);
INSERT INTO sqlite_sequence (name, seq) VALUES ('folklore_progress', 5);
INSERT INTO sqlite_sequence (name, seq) VALUES ('point_transactions', 5);

-- Table: user_progress
CREATE TABLE user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                progress_data TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

INSERT INTO user_progress (id, user_id, category, progress_data, last_updated) VALUES (1, 1, 'quiz', '[{"metadata": {"percentage": 90, "quizId": "cameroon-geography", "quizName": "Cameroon Geography", "score": 9, "total": 10}, "timestamp": "2026-06-01T10:42:15.408Z", "type": "quiz"}, {"type": "quiz", "metadata": {"quizId": "nso_lesson_0_quiz", "lessonId": "nso_lesson_0", "quizName": "Greetings & Basics Quiz", "tribe": "nso", "lessonTitle": "Greetings & Basics", "score": 10, "total": 10, "percentage": 100}, "timestamp": "2026-06-01T10:47:40.131Z"}, {"type": "quiz", "metadata": {"quizId": "nso_lesson_0_quiz_perfect_bonus", "lessonId": "nso_lesson_0", "quizName": "Greetings & Basics Perfect Bonus", "tribe": "nso", "lessonTitle": "Greetings & Basics", "percentage": 100}, "timestamp": "2026-06-01T10:47:40.137Z"}]', '2026-06-01 10:47:40');
INSERT INTO user_progress (id, user_id, category, progress_data, last_updated) VALUES (2, 1, 'lesson', '[{"type": "lesson", "metadata": {"lessonId": "nso_lesson_0", "lessonTitle": "Greetings & Basics", "tribe": "nso"}, "timestamp": "2026-06-01T10:45:59.040Z"}]', '2026-06-01 10:45:59');
INSERT INTO user_progress (id, user_id, category, progress_data, last_updated) VALUES (3, 2, 'quiz', '[{"type": "quiz", "metadata": {"quizId": "cameroon-history", "quizName": "Cameroon History", "score": 10, "total": 10, "percentage": 100}, "timestamp": "2026-06-01T11:17:54.470Z"}]', '2026-06-01 11:17:56');

-- Table: users
CREATE TABLE users (
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
            );

INSERT INTO users (id, first_name, last_name, email, password, country, interest, profile_pic, role, created_at) VALUES (1, 'Banven', 'Eric', 'banven100@gmail.com', 'scrypt:32768:8:1$tiD0ul9AorsJZZRF$89b415daa380c533b8f1efb7678081e44389ff8bde01e941f79b309be474b5d0528e780327336ce53f5a858a48ae6004465ea472a54baf83c82c70ca3b2f37ac', 'Cameroon', 'history', NULL, 'user', '2026-05-27 02:26:00');
INSERT INTO users (id, first_name, last_name, email, password, country, interest, profile_pic, role, created_at) VALUES (2, 'Kester', 'Bill', 'banven10@gmail.com', 'scrypt:32768:8:1$UdwEVlaeYTHELKKo$0b939f82f9ea223e658fff20245a5f3d4382ee31f770b5885c25393cdebfdda8d634f6da17b2c8075f2c9a2a8adc226feab70806fc50754700c626664d123550', 'Cameroon', 'history', NULL, 'user', '2026-06-01 11:16:06');
INSERT INTO users (id, first_name, last_name, email, password, country, interest, profile_pic, role, created_at) VALUES (3, 'eltin', 'ben', 'banven30@gmail.com', 'scrypt:32768:8:1$xgguRLNXMWWpj3jf$c02ca631807d6a3c874493f4363f6b0ab35a2916f06b105dae99f45ed73a38ddf329d3f54cf62595c49960acbcefbe9943735ffd7a38db6ea21613257dc74d1a', 'Cameroon', 'history', NULL, 'user', '2026-06-02 04:16:53');
INSERT INTO users (id, first_name, last_name, email, password, country, interest, profile_pic, role, created_at) VALUES (4, 'NEBA', 'AMBE', 'ambe@gmail.com', 'scrypt:32768:8:1$sksSj9f63Xe98cCQ$7e0c0ea734f5dee02c5df330481758b0fa78be129800f7d55a5332b898fb823ca3cf24f77e3a630b06374cf1cde65b5be11db51310e88fd4aeaee7f4d222fb7d', 'Cameroon', 'CULTURE', NULL, 'user', '2026-06-07 12:30:36');

-- Table: widget_completions
CREATE TABLE widget_completions (
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
            );


-- Table: widgets
CREATE TABLE widgets (
                widget_id TEXT PRIMARY KEY,
                widget_type TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                base_points INTEGER NOT NULL DEFAULT 10,
                difficulty_level INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

INSERT INTO widgets (widget_id, widget_type, name, description, base_points, difficulty_level, is_active, created_at, updated_at) VALUES ('quiz_bamileke_1', 'quiz', 'Bamileke Kingdom Quiz', 'Test your knowledge about the Bamileke kingdom', 20, 2, 1, '2026-06-02 03:19:19', '2026-06-02 03:19:19');
INSERT INTO widgets (widget_id, widget_type, name, description, base_points, difficulty_level, is_active, created_at, updated_at) VALUES ('quiz_bamun_1', 'quiz', 'Bamun Sultanate Quiz', 'Test your knowledge about the Bamun sultanate', 25, 3, 1, '2026-06-02 03:19:19', '2026-06-02 03:19:19');
INSERT INTO widgets (widget_id, widget_type, name, description, base_points, difficulty_level, is_active, created_at, updated_at) VALUES ('lesson_fulani_herdsmen', 'lesson', 'Fulani Herdsmen Traditions', 'Learn about Fulani pastoral traditions', 15, 1, 1, '2026-06-02 03:19:19', '2026-06-02 03:19:19');
INSERT INTO widgets (widget_id, widget_type, name, description, base_points, difficulty_level, is_active, created_at, updated_at) VALUES ('game_tribe_match', 'game', 'Tribe Matching Game', 'Match tribes to their regions', 30, 2, 1, '2026-06-02 03:19:19', '2026-06-02 03:19:19');

