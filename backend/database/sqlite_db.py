"""
SQLite Database for Conversation History, Analytics, and User Authentication.
Stores:
- Users (Credentials, Salt, Role: 'admin' or 'customer')
- Sessions
- Messages (User and Assistant, timestamps, detected language, sources)
- Query Analytics (latency, fallback vs LLM, language stats)
"""

import os
import sqlite3
import json
import hashlib
import secrets
from contextlib import contextmanager
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple


class SQLiteManager:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_dir = os.path.join(base_dir, "data")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "chat_history.db")
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Derives a secure hash using PBKDF2-HMAC-SHA256 with 100,000 iterations."""
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        ).hex()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'customer',
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            # Sessions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            # Messages table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                language TEXT,
                sources TEXT,
                generation_mode TEXT,
                latency_sec REAL,
                sentiment TEXT,
                extracted_info TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
            """)
            # Analytics table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                query_text TEXT,
                detected_language TEXT,
                retrieved_chunks_count INTEGER,
                generation_mode TEXT,
                latency_sec REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()

            # Automatic migration for existing databases
            try:
                cursor.execute("ALTER TABLE sessions ADD COLUMN username TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass

            try:
                cursor.execute("ALTER TABLE messages ADD COLUMN sentiment TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass

            try:
                cursor.execute("ALTER TABLE messages ADD COLUMN extracted_info TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass

        # Seed default demo users if they don't exist
        self._seed_default_users()

    def _seed_default_users(self):
        default_users = [
            ("admin", "admin123", "admin", "System Administrator"),
            ("customer", "customer123", "customer", "Demo Customer")
        ]
        for uname, pwd, role, fname in default_users:
            if not self.get_user(uname):
                self.register_user(uname, pwd, role=role, full_name=fname)

    def register_user(
        self,
        username: str,
        password: str,
        role: str = "customer",
        full_name: str = ""
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Registers a new user with salted PBKDF2 password hashing."""
        username = username.strip().lower()
        if not username:
            return False, "Username cannot be empty.", None
        if len(password) < 4:
            return False, "Password must be at least 4 characters long.", None
        if role not in ("admin", "customer"):
            role = "customer"

        salt = secrets.token_hex(16)
        pwd_hash = self._hash_password(password, salt)

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO users (username, password_hash, salt, role, full_name)
                VALUES (?, ?, ?, ?, ?)
                """, (username, pwd_hash, salt, role, full_name or username.capitalize()))
                conn.commit()

                user_id = cursor.lastrowid
                user_info = {
                    "id": user_id,
                    "username": username,
                    "role": role,
                    "full_name": full_name or username.capitalize()
                }
                return True, "User registered successfully.", user_info
        except sqlite3.IntegrityError:
            return False, f"Username '{username}' already exists. Please choose a different username.", None
        except Exception as e:
            return False, f"Registration error: {str(e)}", None

    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Authenticates username and password against the database."""
        username = username.strip().lower()
        user = self.get_user(username)
        if not user:
            return False, "Invalid username or password.", None

        expected_hash = self._hash_password(password, user["salt"])
        if secrets.compare_digest(expected_hash, user["password_hash"]):
            user_info = {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"],
                "full_name": user["full_name"]
            }
            return True, "Login successful.", user_info
        return False, "Invalid username or password.", None

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username.strip().lower(),))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_or_create_session(self, session_id: str, username: Optional[str] = None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO sessions (session_id, username, created_at, last_active) VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                (session_id, username)
            )
            cursor.execute(
                "UPDATE sessions SET last_active = CURRENT_TIMESTAMP WHERE session_id = ?",
                (session_id,)
            )
            conn.commit()

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        language: Optional[str] = None,
        sources: Optional[List[Dict[str, Any]]] = None,
        generation_mode: Optional[str] = "llm",
        latency_sec: float = 0.0,
        sentiment: Optional[Dict[str, Any]] = None,
        extracted_info: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs
    ):
        username = kwargs.get("username")
        self.get_or_create_session(session_id, username=username)
        sources_json = json.dumps(sources, ensure_ascii=False) if sources else None
        sentiment_json = json.dumps(sentiment, ensure_ascii=False) if sentiment else None
        extracted_info_json = json.dumps(extracted_info, ensure_ascii=False) if extracted_info else None
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO messages (session_id, role, content, language, sources, generation_mode, latency_sec, sentiment, extracted_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (session_id, role, content, language, sources_json, generation_mode, latency_sec, sentiment_json, extracted_info_json))
            conn.commit()

    def log_query_event(
        self,
        session_id: str,
        query: str,
        language: str,
        retrieved_count: int,
        mode: str,
        latency: float
    ):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO analytics_events (session_id, query_text, detected_language, retrieved_chunks_count, generation_mode, latency_sec)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, query, language, retrieved_count, mode, latency))
            conn.commit()

    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content, language, sources, generation_mode, latency_sec, timestamp, sentiment, extracted_info FROM messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,)
            )
            rows = cursor.fetchall()
            messages = []
            for r in rows:
                sentiment_val = None
                if "sentiment" in r.keys() and r["sentiment"]:
                    try:
                        sentiment_val = json.loads(r["sentiment"])
                    except Exception:
                        sentiment_val = r["sentiment"]

                extracted_info_val = None
                if "extracted_info" in r.keys() and r["extracted_info"]:
                    try:
                        extracted_info_val = json.loads(r["extracted_info"])
                    except Exception:
                        extracted_info_val = r["extracted_info"]

                messages.append({
                    "role": r["role"],
                    "content": r["content"],
                    "language": r["language"],
                    "sources": json.loads(r["sources"]) if r["sources"] else [],
                    "generation_mode": r["generation_mode"],
                    "latency_sec": r["latency_sec"],
                    "timestamp": r["timestamp"],
                    "sentiment": sentiment_val,
                    "extracted_info": extracted_info_val
                })
            return messages

    def clear_session(self, session_id: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.commit()

    def get_analytics_summary(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM analytics_events")
            total_queries = cursor.fetchone()[0]

            cursor.execute("SELECT detected_language, COUNT(*) FROM analytics_events GROUP BY detected_language")
            lang_counts = {row[0] or "unknown": row[1] for row in cursor.fetchall()}

            cursor.execute("SELECT generation_mode, COUNT(*) FROM analytics_events GROUP BY generation_mode")
            mode_counts = {row[0] or "unknown": row[1] for row in cursor.fetchall()}

            cursor.execute("SELECT AVG(latency_sec) FROM analytics_events")
            avg_latency = cursor.fetchone()[0] or 0.0

            cursor.execute("SELECT COUNT(DISTINCT session_id) FROM sessions")
            total_sessions = cursor.fetchone()[0]

            return {
                "total_queries": total_queries,
                "total_sessions": total_sessions,
                "language_distribution": lang_counts,
                "generation_mode_distribution": mode_counts,
                "avg_latency_sec": round(avg_latency, 2)
            }
