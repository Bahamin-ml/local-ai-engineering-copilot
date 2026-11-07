"""
ML Engineering Copilot - Database Schema & SQLite Manager
Path: backend/database/models.py
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.config import settings


class DatabaseManager:
    """مدیریت مستقیم و ایمن اتصالات SQLite بدون وابستگی سنگین خارجی"""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or settings.DATABASE_PATH)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # دسترسی به ستون‌ها با نام
        return conn

    def init_db(self) -> None:
        """ساخت جدول‌های نشست‌ها و پیام‌ها در صورت عدم وجود"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. جدول نشست‌ها (Sessions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    summary TEXT DEFAULT ''
                )
            """)

            # 2. جدول پیام‌ها (Messages)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_used TEXT,
                    rag_used INTEGER DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                )
            """)

            # ایندکس‌گذاری برای سرعت بالای بازیابی در طولانی‌مدت
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);")
            conn.commit()

    def create_session(self, session_id: str, title: str = "New ML Chat") -> None:
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO sessions (id, title, updated_at) VALUES (?, ?, ?)",
                (session_id, title, datetime.utcnow())
            )

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT id, title, created_at, updated_at, summary FROM sessions ORDER BY updated_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def save_message(self, session_id: str, role: str, content: str, model_used: str = "", rag_used: bool = False) -> None:
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO messages (session_id, role, content, model_used, rag_used)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, role, content, model_used, 1 if rag_used else 0)
            )
            conn.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (datetime.utcnow(), session_id)
            )

    def get_session_messages(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """بازیابی آخرین پیام‌ها برای تزریق به پنجره زمینه"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT role, content, timestamp, model_used, rag_used
                FROM (
                    SELECT * FROM messages 
                    WHERE session_id = ? 
                    ORDER BY id DESC LIMIT ?
                ) ORDER BY id ASC
                """,
                (session_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_session_summary(self, session_id: str, summary: str) -> None:
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE sessions SET summary = ?, updated_at = ? WHERE id = ?",
                (summary, datetime.utcnow(), session_id)
            )

    def get_session_summary(self, session_id: str) -> str:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT summary FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            return row["summary"] if row and row["summary"] else ""
