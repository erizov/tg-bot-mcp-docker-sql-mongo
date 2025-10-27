#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Progress local server implementation for notes bot.
Uses HTTP API to communicate with a local progress server.
"""

import os
import logging
import uuid
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime


logger = logging.getLogger("notes_bot")
logger.setLevel(logging.INFO)

PROGRESS_SERVER_URL = os.getenv("PROGRESS_SERVER_URL", "http://localhost:8080")


class NotesDatabaseProgressServer:
    """
    Progress local server implementation of notes database.
    Uses HTTP API to communicate with a local progress server.
    """

    def __init__(self) -> None:
        """Initialize progress server connection."""
        self.base_url = PROGRESS_SERVER_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

        # Test connection
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                logger.info("Progress server connected: %s", PROGRESS_SERVER_URL)
            else:
                logger.warning("Progress server health check failed: %s",
                               response.status_code)
        except requests.exceptions.RequestException as e:
            logger.error("Failed to connect to progress server: %s", e)
            raise

    def add_note(self, title: str, content: str, due_at: Optional[str] = None) -> str:
        """Add a new note."""
        note_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        data = {
            "id": note_id,
            "title": title,
            "content": content,
            "due_at": due_at,
            "created_at": created_at
        }

        try:
            response = self.session.post(f"{self.base_url}/notes", json=data)
            response.raise_for_status()
            logger.info("Note added with ID: %s", note_id)
            return note_id
        except requests.exceptions.RequestException as e:
            logger.error("Failed to add note: %s", e)
            raise

    def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Get note by ID."""
        try:
            response = self.session.get(f"{self.base_url}/notes/{note_id}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error("Failed to get note %s: %s", note_id, e)
            raise

    def get_all_notes(self) -> List[Dict[str, Any]]:
        """Get all notes."""
        try:
            response = self.session.get(f"{self.base_url}/notes")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Failed to get all notes: %s", e)
            raise

    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """Search notes by title or content."""
        try:
            response = self.session.get(f"{self.base_url}/notes/search",
                                        params={"q": query})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Failed to search notes: %s", e)
            raise

    def update_note(self, note_id: str, title: Optional[str] = None,
                    content: Optional[str] = None,
                    due_at: Optional[str] = None) -> bool:
        """Update note."""
        data = {}
        if title is not None:
            data["title"] = title
        if content is not None:
            data["content"] = content
        if due_at is not None:
            data["due_at"] = due_at

        if not data:
            return False

        try:
            response = self.session.put(f"{self.base_url}/notes/{note_id}",
                                        json=data)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error("Failed to update note %s: %s", note_id, e)
            return False

    def delete_note(self, note_id: str) -> bool:
        """Delete note."""
        try:
            response = self.session.delete(f"{self.base_url}/notes/{note_id}")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error("Failed to delete note %s: %s", note_id, e)
            return False

    def get_upcoming_reminders(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get upcoming reminders."""
        try:
            response = self.session.get(f"{self.base_url}/notes/reminders",
                                        params={"hours": hours})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Failed to get reminders: %s", e)
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            response = self.session.get(f"{self.base_url}/stats")
            response.raise_for_status()
            stats = response.json()
            stats["database_type"] = "progress_server"
            return stats
        except requests.exceptions.RequestException as e:
            logger.error("Failed to get stats: %s", e)
            raise

    def close(self) -> None:
        """Close database connection."""
        if self.session:
            self.session.close()
            logger.info("Progress server connection closed")
