import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pymongo import MongoClient, ASCENDING, DESCENDING

logger = logging.getLogger("notes_bot")
logger.setLevel(logging.INFO)

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGODB_DB", "notes_db")


class NotesDatabaseMongo:
    """
    Класс для работы с базой данных заметок на MongoDB
    (интерфейс аналогичен NotesDatabase для SQLite)
    """
    def __init__(self) -> None:
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.notes = self.db["notes"]
        self._ensure_indexes()
        logger.info("MongoDB connected: %s, db: %s", MONGO_URI, MONGO_DB)

    def _ensure_indexes(self) -> None:
        self.notes.create_index([
            ("title", ASCENDING),
            ("content", ASCENDING),
            ("due_at", ASCENDING),
            ("created_at", DESCENDING)
        ])

    def add_note(self, title: str, content: str, due_at: Optional[str] = None) -> str:
        note = {
            "title": title,
            "content": content,
            "due_at": due_at,
            "created_at": datetime.now().isoformat(),
        }
        result = self.notes.insert_one(note)
        logger.info(f"Note added (mongo): ID={result.inserted_id}, Title='{title}', Due={due_at}")
        return str(result.inserted_id)

    def delete_note(self, note_id: str) -> bool:
        from bson import ObjectId
        result = self.notes.delete_one({"_id": ObjectId(note_id)})
        if result.deleted_count > 0:
            logger.info(f"Note deleted (mongo): ID={note_id}")
            return True
        logger.warning(f"Attempt to delete non-existent note: ID={note_id}")
        return False

    def search_notes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        results = list(
            self.notes.find({
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"content": {"$regex": query, "$options": "i"}},
                ]
            }).sort("created_at", DESCENDING).limit(limit)
        )
        logger.info(f"Search performed (mongo): query='{query}', results={len(results)}")
        return results

    def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        from bson import ObjectId
        note = self.notes.find_one({"_id": ObjectId(note_id)})
        return note

    def get_recent_notes(self, limit: int = 5) -> List[Dict[str, Any]]:
        notes = list(self.notes.find().sort("created_at", DESCENDING).limit(limit))
        return notes

    def get_upcoming_reminders(self, hours: int = 24) -> List[Dict[str, Any]]:
        now = datetime.now()
        future_time = now + timedelta(hours=hours)
        results = list(self.notes.find({
            "due_at": {"$gte": now.isoformat(), "$lte": future_time.isoformat()}
        }).sort("due_at", ASCENDING))
        return results

    def get_stats(self) -> Dict[str, int]:
        total_notes = self.notes.count_documents({})
        notes_with_reminders = self.notes.count_documents({"due_at": {"$ne": None}})
        notes_without_reminders = self.notes.count_documents({"due_at": None})
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_notes = self.notes.count_documents({"created_at": {"$gte": week_ago}})
        return {
            "total_notes": total_notes,
            "notes_with_reminders": notes_with_reminders,
            "notes_without_reminders": notes_without_reminders,
            "recent_notes": recent_notes
        }

# NOTE: Requires 'pymongo' and 'bson', and correct connection ENV.
