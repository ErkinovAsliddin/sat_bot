# database.py
# Database operations and setup

import sqlite3
from datetime import datetime
import config

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(config.DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_tables()
        self.migrate_database()
        self.add_sample_questions()
        
    def setup_tables(self):
        """Create all necessary tables"""
        # Users table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            total_attempts INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            last_daily TEXT
        )
        ''')
        
        # Questions table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            image_file_id TEXT,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_option TEXT,
            hint TEXT,
            explanation TEXT,
            subject TEXT DEFAULT 'Math',
            topic TEXT
        )
        ''')
        
        # Attempts table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question_id INTEGER,
            user_answer TEXT,
            correct INTEGER,
            timestamp TEXT
        )
        ''')
        
        # Mock sessions table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS mock_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            total_questions INTEGER,
            correct_answers INTEGER,
            sat_score INTEGER,
            timestamp TEXT
        )
        ''')
        
        # Daily questions table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            question_ids TEXT
        )
        ''')
        
        self.conn.commit()
    
    def migrate_database(self):
        """Add any missing columns to existing tables"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
        table_exists = self.cursor.fetchone()
        
        if table_exists:
            self.cursor.execute("PRAGMA table_info(questions)")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            if 'subject' not in columns:
                print("Adding 'subject' column...")
                self.cursor.execute("ALTER TABLE questions ADD COLUMN subject TEXT DEFAULT 'Math'")
                self.conn.commit()
            
            if 'image_file_id' not in columns:
                print("Adding 'image_file_id' column...")
                self.cursor.execute("ALTER TABLE questions ADD COLUMN image_file_id TEXT")
                self.conn.commit()
    
    def add_sample_questions(self):
        """Add sample questions if database is empty"""
        self.cursor.execute("SELECT COUNT(*) FROM questions")
        if self.cursor.fetchone()[0] == 0:
            print("Adding sample questions...")
            sample_questions = [
                ("What is 5 + 7?", None, "10", "12", "13", "14", "B",
                 "Think simple addition", "5+7=12", "Math", "Arithmetic"),
                ("What is 3 × 4?", None, "7", "10", "12", "16", "C",
                 "Multiply the numbers", "3×4=12", "Math", "Multiplication"),
                ("Solve: 2x + 5 = 15", None, "x=5", "x=10", "x=7.5", "x=20", "A",
                 "Isolate x by subtracting 5 then dividing by 2", "2x = 10, so x = 5", "Math", "Algebra"),
                ("Which sentence is correct?", None, "He go to school", "He goes to school", 
                 "He going school", "He gone to school", "B",
                 "Check subject-verb agreement", "Correct form: He goes to school", 
                 "English", "Grammar"),
                ("Choose the correct word: I ____ happy.", None, "am", "is", "are", "be", "A",
                 "First person singular", "I am happy", "English", "Grammar"),
                ("Which is a complete sentence?", None, "Running in the park", "The dog barks loudly", 
                 "Because it was late", "After the game", "B",
                 "A sentence needs a subject and verb", "The dog barks loudly is complete", "English", "Sentence Structure")
            ]
            self.cursor.executemany('''
            INSERT INTO questions (question, image_file_id, option_a, option_b, option_c, option_d, 
                                 correct_option, hint, explanation, subject, topic)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_questions)
            self.conn.commit()
            print(f"Added {len(sample_questions)} sample questions")
    
    def get_user(self, user_id):
        """Get user data"""
        self.cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return self.cursor.fetchone()
    
    def create_user(self, user_id, username):
        """Create new user"""
        self.cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        self.conn.commit()
    
    def update_user_stats(self, user_id, is_correct):
        """Update user statistics"""
        self.cursor.execute(
            "UPDATE users SET total_attempts = total_attempts + 1, correct_answers = correct_answers + ? WHERE user_id = ?",
            (1 if is_correct else 0, user_id)
        )
        self.conn.commit()
    
    def get_random_question(self, subject=None, exclude_id=None):
        """Get random question"""
        if subject and exclude_id:
            self.cursor.execute(
                "SELECT * FROM questions WHERE subject=? AND id != ? ORDER BY RANDOM() LIMIT 1",
                (subject, exclude_id)
            )
        elif subject:
            self.cursor.execute(
                "SELECT * FROM questions WHERE subject=? ORDER BY RANDOM() LIMIT 1",
                (subject,)
            )
        elif exclude_id:
            self.cursor.execute(
                "SELECT * FROM questions WHERE id != ? ORDER BY RANDOM() LIMIT 1",
                (exclude_id,)
            )
        else:
            self.cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 1")
        
        return self.cursor.fetchone()
    
    def get_mock_questions(self, count=20):
        """Get questions for mock test"""
        math_count = count // 2
        english_count = count - math_count
        
        self.cursor.execute(
            "SELECT * FROM questions WHERE subject='Math' ORDER BY RANDOM() LIMIT ?",
            (math_count,)
        )
        math_q = self.cursor.fetchall()
        
        self.cursor.execute(
            "SELECT * FROM questions WHERE subject='English' ORDER BY RANDOM() LIMIT ?",
            (english_count,)
        )
        english_q = self.cursor.fetchall()
        
        return math_q + english_q
    
    def add_question(self, question, image_id, opt_a, opt_b, opt_c, opt_d, 
                     correct, hint, explanation, subject, topic):
        """Add new question to database"""
        self.cursor.execute('''
        INSERT INTO questions (question, image_file_id, option_a, option_b, option_c, option_d,
                             correct_option, hint, explanation, subject, topic)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (question, image_id, opt_a, opt_b, opt_c, opt_d, correct, hint, explanation, subject, topic))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def delete_question(self, question_id):
        """Delete question by ID"""
        self.cursor.execute("DELETE FROM questions WHERE id=?", (question_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_question_by_id(self, question_id):
        """Get specific question by ID"""
        self.cursor.execute("SELECT * FROM questions WHERE id=?", (question_id,))
        return self.cursor.fetchone()
    
    def update_hint_explanation(self, question_id, hint, explanation):
        """Update hint and explanation for a question"""
        self.cursor.execute(
            "UPDATE questions SET hint=?, explanation=? WHERE id=?",
            (hint, explanation, question_id)
        )
        self.conn.commit()
    
    def get_all_questions(self, subject=None):
        """Get all questions, optionally filtered by subject"""
        if subject:
            self.cursor.execute("SELECT * FROM questions WHERE subject=?", (subject,))
        else:
            self.cursor.execute("SELECT * FROM questions")
        return self.cursor.fetchall()
    
    def record_attempt(self, user_id, question_id, user_answer, is_correct):
        """Record user's attempt"""
        self.cursor.execute('''
        INSERT INTO attempts (user_id, question_id, user_answer, correct, timestamp)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, question_id, user_answer, is_correct, datetime.now().isoformat()))
        self.conn.commit()
    
    def save_mock_session(self, user_id, total_questions, correct_answers, sat_score):
        """Save mock test session"""
        self.cursor.execute('''
        INSERT INTO mock_sessions (user_id, total_questions, correct_answers, sat_score, timestamp)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, total_questions, correct_answers, sat_score, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_daily_questions(self, date):
        """Get daily questions for specific date"""
        self.cursor.execute("SELECT question_ids FROM daily_questions WHERE date=?", (date,))
        result = self.cursor.fetchone()
        if result:
            question_ids = [int(qid) for qid in result[0].split(',')]
            questions = []
            for qid in question_ids:
                q = self.get_question_by_id(qid)
                if q:
                    questions.append(q)
            return questions
        return None
    
    def set_daily_questions(self, date, question_ids):
        """Set daily questions for specific date"""
        ids_str = ','.join(map(str, question_ids))
        self.cursor.execute('''
        INSERT OR REPLACE INTO daily_questions (date, question_ids)
        VALUES (?, ?)
        ''', (date, ids_str))
        self.conn.commit()
    
    def get_user_stats(self):
        """Get statistics for all users"""
        self.cursor.execute('''
        SELECT user_id, username, total_attempts, correct_answers, streak
        FROM users
        WHERE total_attempts > 0
        ORDER BY correct_answers DESC
        LIMIT 10
        ''')
        return self.cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        self.conn.close()

# Global database instance
db = Database()
