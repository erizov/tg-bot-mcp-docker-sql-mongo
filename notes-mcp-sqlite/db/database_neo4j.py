#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j database implementation for notes bot.
"""

import os
import logging
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from neo4j import GraphDatabase


logger = logging.getLogger("notes_bot")
logger.setLevel(logging.INFO)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7688")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


class NotesDatabaseNeo4j:
    """
    Neo4j implementation of notes database.
    Uses nodes for notes and relationships for organization.
    """

    def __init__(self) -> None:
        """Initialize Neo4j connection."""
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        self._ensure_constraints()
        logger.info("Neo4j connected: %s, user: %s", NEO4J_URI, NEO4J_USER)

    def _ensure_constraints(self) -> None:
        """Create constraints and indexes."""
        with self.driver.session() as session:
            # Create unique constraint on note id
            session.run("""
                CREATE CONSTRAINT note_id_unique IF NOT EXISTS
                FOR (n:Note) REQUIRE n.id IS UNIQUE
            """)

            # Create index on created_at for performance
            session.run("""
                CREATE INDEX note_created_at IF NOT EXISTS
                FOR (n:Note) ON (n.created_at)
            """)

            # Create index on due_at for reminders
            session.run("""
                CREATE INDEX note_due_at IF NOT EXISTS
                FOR (n:Note) ON (n.due_at)
            """)

    def add_note(self, title: str, content: str, due_at: Optional[str] = None) -> str:
        """Add a new note."""
        note_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        with self.driver.session() as session:
            session.run("""
                CREATE (n:Note {
                    id: $id,
                    title: $title,
                    content: $content,
                    due_at: $due_at,
                    created_at: $created_at
                })
            """, {
                "id": note_id,
                "title": title,
                "content": content,
                "due_at": due_at,
                "created_at": created_at
            })

        logger.info("Note added with ID: %s", note_id)
        return note_id

    def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Get note by ID."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Note {id: $id})
                RETURN n.id as id, n.title as title, n.content as content,
                       n.due_at as due_at, n.created_at as created_at
            """, {"id": note_id})

            record = result.single()
            if record:
                return {
                    "id": record["id"],
                    "title": record["title"],
                    "content": record["content"],
                    "due_at": record["due_at"],
                    "created_at": record["created_at"]
                }
            return None

    def get_all_notes(self) -> List[Dict[str, Any]]:
        """Get all notes."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Note)
                RETURN n.id as id, n.title as title, n.content as content,
                       n.due_at as due_at, n.created_at as created_at
                ORDER BY n.created_at DESC
            """)

            return [
                {
                    "id": record["id"],
                    "title": record["title"],
                    "content": record["content"],
                    "due_at": record["due_at"],
                    "created_at": record["created_at"]
                }
                for record in result
            ]

    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """Search notes by title or content."""
        search_pattern = f".*{query}.*"

        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Note)
                WHERE n.title =~ $pattern OR n.content =~ $pattern
                RETURN n.id as id, n.title as title, n.content as content,
                       n.due_at as due_at, n.created_at as created_at
                ORDER BY n.created_at DESC
            """, {"pattern": search_pattern})

            return [
                {
                    "id": record["id"],
                    "title": record["title"],
                    "content": record["content"],
                    "due_at": record["due_at"],
                    "created_at": record["created_at"]
                }
                for record in result
            ]

    def update_note(self, note_id: str, title: Optional[str] = None,
                    content: Optional[str] = None,
                    due_at: Optional[str] = None) -> bool:
        """Update note."""
        updates = []
        params = {"id": note_id}

        if title is not None:
            updates.append("n.title = $title")
            params["title"] = title

        if content is not None:
            updates.append("n.content = $content")
            params["content"] = content

        if due_at is not None:
            updates.append("n.due_at = $due_at")
            params["due_at"] = due_at

        if not updates:
            return False

        with self.driver.session() as session:
            result = session.run(f"""
                MATCH (n:Note {{id: $id}})
                SET {', '.join(updates)}
                RETURN n.id as id
            """, params)

            return result.single() is not None

    def delete_note(self, note_id: str) -> bool:
        """Delete note."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Note {id: $id})
                WITH n, n.id as id
                DELETE n
                RETURN id
            """, {"id": note_id})

            return result.single() is not None

    def get_upcoming_reminders(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get upcoming reminders."""
        now = datetime.now()
        future_time = now.replace(hour=now.hour + hours)

        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Note)
                WHERE n.due_at IS NOT NULL AND n.due_at >= $now AND n.due_at <= $future
                RETURN n.id as id, n.title as title, n.content as content,
                       n.due_at as due_at, n.created_at as created_at
                ORDER BY n.due_at ASC
            """, {
                "now": now.isoformat(),
                "future": future_time.isoformat()
            })

            return [
                {
                    "id": record["id"],
                    "title": record["title"],
                    "content": record["content"],
                    "due_at": record["due_at"],
                    "created_at": record["created_at"]
                }
                for record in result
            ]

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.driver.session() as session:
            # Total notes
            total_result = session.run("MATCH (n:Note) RETURN count(n) as total")
            total_notes = total_result.single()["total"]

            # Notes with reminders
            reminders_result = session.run("""
                MATCH (n:Note) WHERE n.due_at IS NOT NULL
                RETURN count(n) as with_reminders
            """)
            with_reminders = reminders_result.single()["with_reminders"]

            # Notes without reminders
            no_reminders_result = session.run("""
                MATCH (n:Note) WHERE n.due_at IS NULL
                RETURN count(n) as without_reminders
            """)
            without_reminders = no_reminders_result.single()["without_reminders"]

            return {
                "total_notes": total_notes,
                "notes_with_reminders": with_reminders,
                "notes_without_reminders": without_reminders,
                "database_type": "neo4j"
            }

    def close(self) -> None:
        """Close database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
