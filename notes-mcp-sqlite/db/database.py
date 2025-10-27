#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для работы с базой данных заметок.
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from pathlib import Path

# Refactored: moved logging setup and logger to the module level
logger = logging.getLogger("notes_bot")
logger.setLevel(logging.INFO)

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

file_handler = logging.FileHandler(
    log_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log", encoding="utf-8"
)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


class NotesDatabase:
    """Класс для работы с базой данных заметок."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Инициализация базы данных."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                due_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

    def add_note(self, title: str, content: str, due_at: Optional[str] = None) -> int:
        """Добавляет новую заметку."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO notes (title, content, due_at)
            VALUES (?, ?, ?)
            """,
            (title, content, due_at)
        )
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Note added: ID={note_id}, Title='{title}', Due={due_at}")
        return note_id

    def delete_note(self, note_id: int) -> bool:
        """Удаляет заметку по ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
        if not cursor.fetchone():
            conn.close()
            logger.warning(f"Attempt to delete non-existent note: ID={note_id}")
            return False
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        if deleted_count > 0:
            logger.info(f"Note deleted: ID={note_id}")
            return True
        return False

    def search_notes(self, query: str, limit: int = 10) -> List[Tuple]:
        """Ищет заметки по содержимому."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        search_pattern = f"%{query}%"
        cursor.execute(
            """
            SELECT id, title, content, due_at, created_at
            FROM notes
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (search_pattern, search_pattern, limit)
        )
        results = cursor.fetchall()
        conn.close()
        logger.info(f"Search performed: query='{query}', results={len(results)}")
        return results

    def get_note_by_id(self, note_id: int) -> Optional[Tuple]:
        """Получает заметку по ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, title, content, due_at, created_at
            FROM notes
            WHERE id = ?
            """,
            (note_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result

    def get_recent_notes(self, limit: int = 5) -> List[Tuple]:
        """Получает последние заметки."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, title, content, due_at, created_at
            FROM notes
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        notes = cursor.fetchall()
        conn.close()
        return notes

    def get_upcoming_reminders(self, hours: int = 24) -> List[Tuple]:
        """Получает напоминания на ближайшие часы."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now()
        future_time = now + timedelta(hours=hours)
        cursor.execute(
            """
            SELECT id, title, content, due_at, created_at
            FROM notes
            WHERE due_at IS NOT NULL
            AND due_at BETWEEN ? AND ?
            ORDER BY due_at ASC
            """,
            (now.strftime("%Y-%m-%d %H:%M:%S"), future_time.strftime("%Y-%m-%d %H:%M:%S"))
        )
        reminders = cursor.fetchall()
        conn.close()
        return reminders

    def get_stats(self) -> dict:
        """Получает статистику по заметкам."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM notes")
        total_notes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM notes WHERE due_at IS NOT NULL")
        notes_with_reminders = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM notes WHERE due_at IS NULL")
        notes_without_reminders = cursor.fetchone()[0]
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("SELECT COUNT(*) FROM notes WHERE created_at >= ?", (week_ago,))
        recent_notes = cursor.fetchone()[0]
        conn.close()
        return {
            "total_notes": total_notes,
            "notes_with_reminders": notes_with_reminders,
            "notes_without_reminders": notes_without_reminders,
            "recent_notes": recent_notes
        }
