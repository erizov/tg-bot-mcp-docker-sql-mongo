#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL database implementation for notes bot.
Uses psycopg2 for database connectivity.
"""

import os
import logging
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
from datetime import datetime


logger = logging.getLogger("notes_bot")
logger.setLevel(logging.INFO)

POSTGRESQL_HOST = os.getenv("POSTGRESQL_HOST", "localhost")
POSTGRESQL_PORT = os.getenv("POSTGRESQL_PORT", "5432")
POSTGRESQL_DB = os.getenv("POSTGRESQL_DB", "notes_db")
POSTGRESQL_USER = os.getenv("POSTGRESQL_USER", "postgres")
POSTGRESQL_PASSWORD = os.getenv("POSTGRESQL_PASSWORD", "password")


class NotesDatabasePostgreSQL:
    """
    PostgreSQL implementation of notes database.
    Uses standard SQL tables for notes storage.
    """

    def __init__(self) -> None:
        """Initialize PostgreSQL connection."""
        self.connection = None
        self._connect()
        self._ensure_tables()
        logger.info("PostgreSQL connected: %s:%s/%s, user: %s",
                    POSTGRESQL_HOST, POSTGRESQL_PORT, POSTGRESQL_DB,
                    POSTGRESQL_USER)

    def _connect(self) -> None:
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(
                host=POSTGRESQL_HOST,
                port=POSTGRESQL_PORT,
                database=POSTGRESQL_DB,
                user=POSTGRESQL_USER,
                password=POSTGRESQL_PASSWORD
            )
            self.connection.autocommit = True
        except psycopg2.Error as e:
            logger.error("Failed to connect to PostgreSQL: %s", e)
            raise

    def _ensure_tables(self) -> None:
        """Create tables if they don't exist."""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id VARCHAR(36) PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    due_at TIMESTAMP,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notes_created_at
                ON notes(created_at)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notes_due_at
                ON notes(due_at)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notes_title
                ON notes USING gin(to_tsvector('english', title))
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notes_content
                ON notes USING gin(to_tsvector('english', content))
            """)

    def add_note(self, title: str, content: str, due_at: Optional[str] = None) -> str:
        """Add a new note."""
        note_id = str(uuid.uuid4())
        created_at = datetime.now()

        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO notes (id, title, content, due_at, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (note_id, title, content, due_at, created_at))

        logger.info("Note added with ID: %s", note_id)
        return note_id

    def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Get note by ID."""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, title, content, due_at, created_at
                FROM notes WHERE id = %s
            """, (note_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_all_notes(self) -> List[Dict[str, Any]]:
        """Get all notes."""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, title, content, due_at, created_at
                FROM notes ORDER BY created_at DESC
            """)

            return [dict(row) for row in cursor.fetchall()]

    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """Search notes by title or content using full-text search."""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, title, content, due_at, created_at
                FROM notes
                WHERE to_tsvector('english', title || ' ' || content)
                      @@ plainto_tsquery('english', %s)
                ORDER BY created_at DESC
            """, (query,))

            return [dict(row) for row in cursor.fetchall()]

    def update_note(self, note_id: str, title: Optional[str] = None,
                    content: Optional[str] = None,
                    due_at: Optional[str] = None) -> bool:
        """Update note."""
        updates = []
        params = []

        if title is not None:
            updates.append("title = %s")
            params.append(title)

        if content is not None:
            updates.append("content = %s")
            params.append(content)

        if due_at is not None:
            updates.append("due_at = %s")
            params.append(due_at)

        if not updates:
            return False

        params.append(note_id)

        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE notes SET {', '.join(updates)}
                WHERE id = %s
            """, params)

            return cursor.rowcount > 0

    def delete_note(self, note_id: str) -> bool:
        """Delete note."""
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
            return cursor.rowcount > 0

    def get_upcoming_reminders(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get upcoming reminders."""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, title, content, due_at, created_at
                FROM notes
                WHERE due_at IS NOT NULL
                  AND due_at >= CURRENT_TIMESTAMP
                  AND due_at <= CURRENT_TIMESTAMP + INTERVAL '%s hours'
                ORDER BY due_at ASC
            """, (hours,))

            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.connection.cursor() as cursor:
            # Total notes
            cursor.execute("SELECT COUNT(*) FROM notes")
            total_notes = cursor.fetchone()[0]

            # Notes with reminders
            cursor.execute("""
                SELECT COUNT(*) FROM notes WHERE due_at IS NOT NULL
            """)
            notes_with_reminders = cursor.fetchone()[0]

            # Notes without reminders
            cursor.execute("""
                SELECT COUNT(*) FROM notes WHERE due_at IS NULL
            """)
            notes_without_reminders = cursor.fetchone()[0]

            return {
                "total_notes": total_notes,
                "notes_with_reminders": notes_with_reminders,
                "notes_without_reminders": notes_without_reminders,
                "database_type": "postgresql"
            }

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("PostgreSQL connection closed")
