# desktop/services/session_store.py

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class SessionRecord:
    session_id: str
    title: str
    created_at: str


@dataclass
class MessageRecord:
    id: int
    session_id: str
    role: str
    content: str
    created_at: str


class SessionStore:
    """SQLite persistence for chat sessions and their messages."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.db_path), timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _init(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id)
                        REFERENCES sessions(session_id)
                        ON DELETE CASCADE
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_messages_session_id
                ON messages(session_id, id)
                """
            )

    def list_sessions(self) -> List[SessionRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT session_id, title, created_at
                FROM sessions
                ORDER BY created_at DESC
                """
            ).fetchall()

        return [
            SessionRecord(
                session_id=row["session_id"],
                title=row["title"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get(self, session_id: str) -> Optional[SessionRecord]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT session_id, title, created_at
                FROM sessions
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()

        if row is None:
            return None

        return SessionRecord(
            session_id=row["session_id"],
            title=row["title"],
            created_at=row["created_at"],
        )

    def upsert(
        self,
        session_id: str,
        title: str,
        created_at: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO sessions (session_id, title, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    title = excluded.title
                """,
                (session_id, title, created_at),
            )

    def delete(self, session_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM sessions WHERE session_id = ?",
                (session_id,),
            )

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        created_at: str,
    ) -> int:
        """Save one message and return its database ID."""

        if role not in {"user", "assistant", "system"}:
            raise ValueError(
                "role must be one of: 'user', 'assistant', or 'system'"
            )

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO messages (session_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, role, content, created_at),
            )
            return int(cursor.lastrowid)

    def list_messages(self, session_id: str) -> List[MessageRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, session_id, role, content, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()

        return [
            MessageRecord(
                id=row["id"],
                session_id=row["session_id"],
                role=row["role"],
                content=row["content"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def delete_messages(self, session_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM messages WHERE session_id = ?",
                (session_id,),
            )
