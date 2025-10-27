import os
import logging
from typing import Any

logger = logging.getLogger("notes_bot")

USE_DB_BACKEND = os.getenv("USE_DB_BACKEND", "sqlite")

NotesDatabaseClass: Any = None

try:
    if USE_DB_BACKEND == "mongo":
        from db.database_mongo import NotesDatabaseMongo
        NotesDatabaseClass = NotesDatabaseMongo
    elif USE_DB_BACKEND == "progress":
        from db.database_progress import NotesDatabaseProgress
        NotesDatabaseClass = NotesDatabaseProgress
    else:
        from db.database import NotesDatabase
        NotesDatabaseClass = NotesDatabase
    logger.info(f"Selected DB backend: {USE_DB_BACKEND}")
except ImportError as e:
    logger.error(f"Failed to import DB backend '{USE_DB_BACKEND}': {e}")
    raise

def get_database(*args, **kwargs) -> Any:
    """
    Factory method for environment-driven NotesDB backend selection.
    Args are passed to the selected class constructor (usually db path or none).
    """
    return NotesDatabaseClass(*args, **kwargs)
