import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict, Any
import uuid

logger = logging.getLogger("notes_bot")
logger.setLevel(logging.INFO)

class NotesDatabaseProgress:
    """In-memory progress database version for notes (for tests/dev)."""
    def __init__(self) -> None:
        self.notes: Dict[str, Dict[str, Any]] = {}
        logger.info("Progress in-memory NotesDatabase initialized.")

    def add_note(self, title: str, content: str, due_at: Optional[str] = None) -> str:
        note_id = str(uuid.uuid4())
        note = {
            "id": note_id,
            "title": title,
            "content": content,
            "due_at": due_at,
            "created_at": datetime.now().isoformat()
        }
        self.notes[note_id] = note
        logger.info(f"Note added (progress): ID={note_id}, Title='{title}', Due={due_at}")
        return note_id

    def delete_note(self, note_id: str) -> bool:
        if note_id in self.notes:
            del self.notes[note_id]
            logger.info(f"Note deleted (progress): ID={note_id}")
            return True
        logger.warning(f"Attempt to delete non-existent note (progress): ID={note_id}")
        return False

    def search_notes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        res = [note for note in self.notes.values()
               if query.lower() in note["title"].lower() or query.lower() in note["content"].lower()]
        logger.info(f"Search performed (progress): query='{query}', results={len(res)}")
        return sorted(res, key=lambda n: n["created_at"], reverse=True)[:limit]

    def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        return self.notes.get(note_id)

    def get_recent_notes(self, limit: int = 5) -> List[Dict[str, Any]]:
        notes_sorted = sorted(self.notes.values(), key=lambda n: n["created_at"], reverse=True)
        return notes_sorted[:limit]

    def get_upcoming_reminders(self, hours: int = 24) -> List[Dict[str, Any]]:
        now = datetime.now()
        future_time = now + timedelta(hours=hours)
        result = []
        for note in self.notes.values():
            due_at_str = note.get("due_at")
            if due_at_str:
                try:
                    due_at = datetime.fromisoformat(due_at_str)
                    if now <= due_at <= future_time:
                        result.append(note)
                except ValueError:
                    continue
        return sorted(result, key=lambda n: n["due_at"])

    def get_stats(self) -> Dict[str, int]:
        total_notes = len(self.notes)
        notes_with_reminders = sum(1 for n in self.notes.values() if n["due_at"])
        notes_without_reminders = total_notes - notes_with_reminders
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_notes = sum(1 for n in self.notes.values() if n["created_at"] >= week_ago)
        return {
            "total_notes": total_notes,
            "notes_with_reminders": notes_with_reminders,
            "notes_without_reminders": notes_without_reminders,
            "recent_notes": recent_notes
        }
