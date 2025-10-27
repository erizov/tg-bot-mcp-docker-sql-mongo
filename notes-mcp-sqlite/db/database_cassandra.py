#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cassandra database implementation for notes bot.
Uses cassandra-driver for database connectivity.
"""

import os
import logging
import uuid
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime

# Check Python version compatibility
if sys.version_info >= (3, 13):
    logger = logging.getLogger("notes_bot")
    logger.error("Cassandra driver is not compatible with Python 3.13+ due to removed asyncore module")
    logger.error("Please use Python 3.8-3.12 for Cassandra support")
    raise ImportError("Cassandra driver not compatible with Python 3.13+")

try:
    from cassandra.cluster import Cluster
    from cassandra.auth import PlainTextAuthProvider
    from cassandra.query import SimpleStatement
except ImportError as e:
    logger = logging.getLogger("notes_bot")
    logger.error(f"Failed to import Cassandra driver: {e}")
    raise ImportError(f"Cassandra driver not available: {e}")


logger = logging.getLogger("notes_bot")
logger.setLevel(logging.INFO)

CASSANDRA_HOSTS = os.getenv("CASSANDRA_HOSTS", "localhost").split(",")
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT", "9042"))
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "notes_keyspace")
CASSANDRA_USER = os.getenv("CASSANDRA_USER", "")
CASSANDRA_PASSWORD = os.getenv("CASSANDRA_PASSWORD", "")


class NotesDatabaseCassandra:
    """
    Cassandra implementation of notes database.
    Uses wide-column store for notes storage.
    """

    def __init__(self) -> None:
        """Initialize Cassandra connection."""
        self.cluster = None
        self.session = None
        self._connect()
        self._ensure_keyspace_and_table()
        logger.info("Cassandra connected: %s:%s/%s, user: %s",
                    CASSANDRA_HOSTS, CASSANDRA_PORT, CASSANDRA_KEYSPACE,
                    CASSANDRA_USER or "anonymous")

    def _connect(self) -> None:
        """Establish database connection."""
        try:
            if CASSANDRA_USER and CASSANDRA_PASSWORD:
                auth_provider = PlainTextAuthProvider(
                    username=CASSANDRA_USER,
                    password=CASSANDRA_PASSWORD
                )
                self.cluster = Cluster(
                    CASSANDRA_HOSTS,
                    port=CASSANDRA_PORT,
                    auth_provider=auth_provider
                )
            else:
                self.cluster = Cluster(CASSANDRA_HOSTS, port=CASSANDRA_PORT)

            self.session = self.cluster.connect()
        except Exception as e:
            logger.error("Failed to connect to Cassandra: %s", e)
            raise

    def _ensure_keyspace_and_table(self) -> None:
        """Create keyspace and table if they don't exist."""
        # Create keyspace
        self.session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
            WITH REPLICATION = {{
                'class': 'SimpleStrategy',
                'replication_factor': 1
            }}
        """)

        # Use the keyspace
        self.session.set_keyspace(CASSANDRA_KEYSPACE)

        # Create table
        self.session.execute(f"""
            CREATE TABLE IF NOT EXISTS notes (
                id UUID PRIMARY KEY,
                title TEXT,
                content TEXT,
                due_at TIMESTAMP,
                created_at TIMESTAMP
            )
        """)

        # Create indexes for performance
        self.session.execute(f"""
            CREATE INDEX IF NOT EXISTS notes_title_idx
            ON notes (title)
        """)

        self.session.execute(f"""
            CREATE INDEX IF NOT EXISTS notes_created_at_idx
            ON notes (created_at)
        """)

        self.session.execute(f"""
            CREATE INDEX IF NOT EXISTS notes_due_at_idx
            ON notes (due_at)
        """)

    def add_note(self, title: str, content: str, due_at: Optional[str] = None) -> str:
        """Add a new note."""
        note_id = str(uuid.uuid4())
        created_at = datetime.now()

        query = """
            INSERT INTO notes (id, title, content, due_at, created_at)
            VALUES (?, ?, ?, ?, ?)
        """

        self.session.execute(query, (
            uuid.UUID(note_id),
            title,
            content,
            datetime.fromisoformat(due_at) if due_at else None,
            created_at
        ))

        logger.info("Note added with ID: %s", note_id)
        return note_id

    def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Get note by ID."""
        query = "SELECT id, title, content, due_at, created_at FROM notes WHERE id = ?"
        result = self.session.execute(query, (uuid.UUID(note_id),))

        row = result.one()
        if row:
            return {
                "id": str(row.id),
                "title": row.title,
                "content": row.content,
                "due_at": row.due_at.isoformat() if row.due_at else None,
                "created_at": row.created_at.isoformat()
            }
        return None

    def get_all_notes(self) -> List[Dict[str, Any]]:
        """Get all notes."""
        query = "SELECT id, title, content, due_at, created_at FROM notes"
        result = self.session.execute(query)

        return [
            {
                "id": str(row.id),
                "title": row.title,
                "content": row.content,
                "due_at": row.due_at.isoformat() if row.due_at else None,
                "created_at": row.created_at.isoformat()
            }
            for row in result
        ]

    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """Search notes by title or content."""
        # Cassandra doesn't have built-in full-text search, so we'll do a simple LIKE search
        search_query = """
            SELECT id, title, content, due_at, created_at FROM notes
            WHERE title CONTAINS ? OR content CONTAINS ?
            ALLOW FILTERING
        """

        result = self.session.execute(search_query, (query, query))

        return [
            {
                "id": str(row.id),
                "title": row.title,
                "content": row.content,
                "due_at": row.due_at.isoformat() if row.due_at else None,
                "created_at": row.created_at.isoformat()
            }
            for row in result
        ]

    def update_note(self, note_id: str, title: Optional[str] = None,
                    content: Optional[str] = None,
                    due_at: Optional[str] = None) -> bool:
        """Update note."""
        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)

        if content is not None:
            updates.append("content = ?")
            params.append(content)

        if due_at is not None:
            updates.append("due_at = ?")
            params.append(datetime.fromisoformat(due_at))

        if not updates:
            return False

        params.append(uuid.UUID(note_id))

        query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"
        result = self.session.execute(query, params)

        return True  # Cassandra doesn't return row count

    def delete_note(self, note_id: str) -> bool:
        """Delete note."""
        query = "DELETE FROM notes WHERE id = ?"
        self.session.execute(query, (uuid.UUID(note_id),))
        return True  # Cassandra doesn't return row count

    def get_upcoming_reminders(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get upcoming reminders."""
        now = datetime.now()
        future_time = now.replace(hour=now.hour + hours)

        query = """
            SELECT id, title, content, due_at, created_at FROM notes
            WHERE due_at >= ? AND due_at <= ?
            ALLOW FILTERING
        """

        result = self.session.execute(query, (now, future_time))

        return [
            {
                "id": str(row.id),
                "title": row.title,
                "content": row.content,
                "due_at": row.due_at.isoformat() if row.due_at else None,
                "created_at": row.created_at.isoformat()
            }
            for row in result
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        # Total notes
        total_result = self.session.execute("SELECT COUNT(*) FROM notes")
        total_notes = total_result.one().count

        # Notes with reminders
        reminders_result = self.session.execute(
            "SELECT COUNT(*) FROM notes WHERE due_at IS NOT NULL ALLOW FILTERING"
        )
        notes_with_reminders = reminders_result.one().count

        # Notes without reminders
        no_reminders_result = self.session.execute(
            "SELECT COUNT(*) FROM notes WHERE due_at IS NULL ALLOW FILTERING"
        )
        notes_without_reminders = no_reminders_result.one().count

        return {
            "total_notes": total_notes,
            "notes_with_reminders": notes_with_reminders,
            "notes_without_reminders": notes_without_reminders,
            "database_type": "cassandra"
        }

    def close(self) -> None:
        """Close database connection."""
        if self.session:
            self.session.shutdown()
        if self.cluster:
            self.cluster.shutdown()
        logger.info("Cassandra connection closed")
