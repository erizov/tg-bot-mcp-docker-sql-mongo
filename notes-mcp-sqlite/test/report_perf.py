import os
import sys
import time
import logging
from typing import Dict, List, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db.database_selector import get_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("perf_report")

BACKENDS = ["sqlite", "progress"]
try:
    import pymongo
    BACKENDS.append("mongo")
except ImportError:
    logger.warning("MongoDB backend skipped (pymongo not installed)")

COUNT = 500  # manageable for perf in dev

def bench(backend: str, notes_db_path: str = "notes.db") -> Dict[str, Any]:
    os.environ["USE_DB_BACKEND"] = backend
    db = get_database(notes_db_path)
    t0 = time.perf_counter()
    ids = []
    for i in range(COUNT):
        ids.append(db.add_note(f"T{i}", f"Performance test record {i}", due_at=None))
    t_insert = time.perf_counter() - t0
    t1 = time.perf_counter()
    for test_id in ids:
        _ = db.get_note_by_id(test_id)
    t_lookup = time.perf_counter() - t1
    t_stats = db.get_stats()
    logger.info(f"Backend {backend}: Insert {t_insert:.3f}s, Lookup {t_lookup:.3f}s, Stats: {t_stats}")
    return {"backend": backend, "insert_time": t_insert, "lookup_time": t_lookup, "total_notes": t_stats["total_notes"]}

def render_html(results: List[Dict[str, Any]]) -> str:
    rows = "".join(f"<tr><td>{r['backend']}</td><td>{r['insert_time']:.2f}</td><td>{r['lookup_time']:.2f}</td><td>{r['total_notes']}</td></tr>" for r in results)
    return f"""<html><head><title>DB Perf Report</title><link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css'></head><body><div class='container'><h2>Performance DB Backends</h2><table class='table'><thead><tr><th>Backend</th><th>Insert time (s, {COUNT} records)</th><th>Lookup time (s, {COUNT} records)</th><th>Total notes</th></tr></thead><tbody>{rows}</tbody></table></div></body></html>"""

def main():
    results: List[Dict[str, Any]] = []
    for backend in BACKENDS:
        try:
            results.append(bench(backend))
        except Exception as e:
            logger.error(f"Error benchmarking {backend}: {e}")

    html = render_html(results)
    outname = "db_perf_report.html"
    with open(outname, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Performance report written to {outname}")

if __name__ == "__main__":
    main()
