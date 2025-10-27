import os
import logging
from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse, JSONResponse
from db.database_selector import get_database, USE_DB_BACKEND

logger = logging.getLogger("notes_bot")
logger.setLevel(logging.INFO)

app = FastAPI(title="Notes DB Monitor", version="1.0")
db = get_database(os.getenv("NOTES_DB_PATH", "notes.db"))

@app.get("/health")
def health():
    logger.info("/health endpoint accessed.")
    return {"ok": True, "db_backend": USE_DB_BACKEND}

@app.get("/count", response_class=JSONResponse)
def db_count():
    try:
        n = db.get_stats()["total_notes"]
    except Exception as e:
        logger.error(f"Error in /count: {e}")
        n = None
    return {"records": n, "backend": USE_DB_BACKEND}

@app.get("/count/html", response_class=HTMLResponse)
def db_count_html():
    try:
        n = db.get_stats()["total_notes"]
    except Exception as e:
        logger.error(f"Error in /count/html: {e}")
        n = None
    body = f"""<div class='container'><h3>Notes DB Count</h3><table class='table'><tr><th>Backend</th><td>{USE_DB_BACKEND}</td></tr><tr><th>Records</th><td>{n}</td></tr></table></div>"""
    return f"""<html><head><link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css'></head><body>{body}</body></html>"""
