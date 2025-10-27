import unittest
import logging
import os
import sys
import time
from datetime import datetime, timedelta

# --- PATCH sys.path for correct relative db imports ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # noqa: E402

try:
    from db.database_mongo import NotesDatabaseMongo  # noqa: E402
    MONGO_AVAILABLE = True
except ImportError:
    NotesDatabaseMongo = None
    MONGO_AVAILABLE = False

try:
    from db.database_neo4j import NotesDatabaseNeo4j  # noqa: E402
    NEO4J_AVAILABLE = True
except ImportError:
    NotesDatabaseNeo4j = None
    NEO4J_AVAILABLE = False

try:
    from db.database_postgresql import NotesDatabasePostgreSQL  # noqa: E402
    POSTGRESQL_AVAILABLE = True
except ImportError:
    NotesDatabasePostgreSQL = None
    POSTGRESQL_AVAILABLE = False

try:
    from db.database_cassandra import NotesDatabaseCassandra  # noqa: E402
    CASSANDRA_AVAILABLE = True
except ImportError:
    NotesDatabaseCassandra = None
    CASSANDRA_AVAILABLE = False

from db.database_progress import NotesDatabaseProgress  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_test")


class NotesDBTestCase(unittest.TestCase):
    def setUp(self):
        self.db = NotesDatabaseProgress()
        logger.info("Progress DB set up for unit test.")

    def test_add_and_get(self):
        note_id = self.db.add_note("TestTitle", "Test content")
        note = self.db.get_note_by_id(note_id)
        self.assertIsNotNone(note)
        self.assertEqual(note["title"], "TestTitle")

    def test_delete(self):
        note_id = self.db.add_note("ForDelete", "Content")
        self.assertTrue(self.db.delete_note(note_id))
        self.assertFalse(self.db.delete_note(note_id))

    def test_search(self):
        self.db.add_note("Foo", "Bar")
        self.db.add_note("Baz", "Qux")
        results = self.db.search_notes("Foo")
        self.assertTrue(any(n["title"] == "Foo" for n in results))

    def test_stats(self):
        self.db.add_note("T1", "C1", due_at=datetime.now().isoformat())
        self.db.add_note("T2", "C2")
        stats = self.db.get_stats()
        self.assertEqual(stats["total_notes"], 2)

    def test_reminders(self):
        due_time = (datetime.now() + timedelta(seconds=10)).isoformat()
        self.db.add_note("WithRemind", "R", due_at=due_time)
        reminders = self.db.get_upcoming_reminders(1)  # 1 hour window
        self.assertTrue(any(n["title"] == "WithRemind" for n in reminders))


@unittest.skipUnless(MONGO_AVAILABLE, "PyMongo not installed")
class MongoDBTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.mongo = NotesDatabaseMongo()
            cls.working = True
        except Exception as e:
            logger.error(f"MongoDB unavailable: {e}")
            cls.working = False

    def setUp(self):
        if self.working:
            self.db = self.mongo
            # Wipe collection
            self.db.notes.delete_many({})
            logger.info("MongoDB wiped for unit test.")

    def test_add_and_get(self):
        note_id = self.db.add_note("MT", "Mongo text")
        note = self.db.get_note_by_id(note_id)
        self.assertIsNotNone(note)
        self.assertEqual(note["title"], "MT")

    def test_delete(self):
        note_id = self.db.add_note("D", "Del")
        self.assertTrue(self.db.delete_note(note_id))

    def test_search(self):
        self.db.add_note("QuickTest", "Fast")
        res = self.db.search_notes("QuickTest")
        self.assertTrue(any(n["title"] == "QuickTest" for n in res))

    def test_stats(self):
        self.db.add_note("S1", "S", due_at=datetime.now().isoformat())
        self.db.add_note("S2", "S")
        stats = self.db.get_stats()
        self.assertGreaterEqual(stats["total_notes"], 2)

    def test_reminders(self):
        due_time = (datetime.now() + timedelta(seconds=10)).isoformat()
        self.db.add_note("MongoRemind", "remind", due_at=due_time)
        reminders = self.db.get_upcoming_reminders(1)
        self.assertTrue(any(n["title"] == "MongoRemind" for n in reminders))


@unittest.skipUnless(NEO4J_AVAILABLE, "Neo4j driver not installed")
class Neo4jTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.neo4j = NotesDatabaseNeo4j()
            cls.working = True
        except Exception as e:
            logger.error(f"Neo4j unavailable: {e}")
            cls.working = False

    def setUp(self):
        if self.working:
            self.db = self.neo4j
            # Clear all notes
            with self.db.driver.session() as session:
                session.run("MATCH (n:Note) DELETE n")
            logger.info("Neo4j wiped for unit test.")

    def test_add_and_get(self):
        note_id = self.db.add_note("Neo4jTest", "Neo4j content")
        note = self.db.get_note_by_id(note_id)
        self.assertIsNotNone(note)
        self.assertEqual(note["title"], "Neo4jTest")

    def test_delete(self):
        note_id = self.db.add_note("Neo4jDelete", "Delete test")
        self.assertTrue(self.db.delete_note(note_id))

    def test_search(self):
        self.db.add_note("Neo4jSearch", "Search test")
        res = self.db.search_notes("Neo4jSearch")
        self.assertTrue(any(n["title"] == "Neo4jSearch" for n in res))

    def test_stats(self):
        self.db.add_note("Neo4jS1", "Stats", due_at=datetime.now().isoformat())
        self.db.add_note("Neo4jS2", "Stats")
        stats = self.db.get_stats()
        self.assertGreaterEqual(stats["total_notes"], 2)

    def test_reminders(self):
        due_time = (datetime.now() + timedelta(seconds=10)).isoformat()
        self.db.add_note("Neo4jRemind", "remind", due_at=due_time)
        reminders = self.db.get_upcoming_reminders(1)
        self.assertTrue(any(n["title"] == "Neo4jRemind" for n in reminders))


@unittest.skipUnless(POSTGRESQL_AVAILABLE, "PostgreSQL driver not installed")
class PostgreSQLTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.postgresql = NotesDatabasePostgreSQL()
            cls.working = True
        except Exception as e:
            logger.error(f"PostgreSQL unavailable: {e}")
            cls.working = False

    def setUp(self):
        if self.working:
            self.db = self.postgresql
            # Clear all notes
            try:
                notes = self.db.get_all_notes()
                for note in notes:
                    self.db.delete_note(note["id"])
            except Exception:
                pass  # Database might not have any notes
            logger.info("PostgreSQL wiped for unit test.")

    def test_add_and_get(self):
        note_id = self.db.add_note("PostgreSQLTest", "PostgreSQL content")
        note = self.db.get_note_by_id(note_id)
        self.assertIsNotNone(note)
        self.assertEqual(note["title"], "PostgreSQLTest")

    def test_delete(self):
        note_id = self.db.add_note("PostgreSQLDelete", "Delete test")
        self.assertTrue(self.db.delete_note(note_id))

    def test_search(self):
        self.db.add_note("PostgreSQLSearch", "Search test")
        res = self.db.search_notes("PostgreSQLSearch")
        self.assertTrue(any(n["title"] == "PostgreSQLSearch" for n in res))

    def test_stats(self):
        self.db.add_note("PostgreSQLS1", "Stats", due_at=datetime.now().isoformat())
        self.db.add_note("PostgreSQLS2", "Stats")
        stats = self.db.get_stats()
        self.assertGreaterEqual(stats["total_notes"], 2)

    def test_reminders(self):
        due_time = (datetime.now() + timedelta(seconds=10)).isoformat()
        self.db.add_note("PostgreSQLRemind", "remind", due_at=due_time)
        reminders = self.db.get_upcoming_reminders(1)
        self.assertTrue(any(n["title"] == "PostgreSQLRemind" for n in reminders))


@unittest.skipUnless(CASSANDRA_AVAILABLE, "Cassandra driver not installed")
class CassandraTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.cassandra = NotesDatabaseCassandra()
            cls.working = True
        except Exception as e:
            logger.error(f"Cassandra unavailable: {e}")
            cls.working = False

    def setUp(self):
        if self.working:
            self.db = self.cassandra
            # Clear all notes
            try:
                notes = self.db.get_all_notes()
                for note in notes:
                    self.db.delete_note(note["id"])
            except Exception:
                pass  # Database might not have any notes
            logger.info("Cassandra wiped for unit test.")

    def test_add_and_get(self):
        note_id = self.db.add_note("CassandraTest", "Cassandra content")
        note = self.db.get_note_by_id(note_id)
        self.assertIsNotNone(note)
        self.assertEqual(note["title"], "CassandraTest")

    def test_delete(self):
        note_id = self.db.add_note("CassandraDelete", "Delete test")
        self.assertTrue(self.db.delete_note(note_id))

    def test_search(self):
        self.db.add_note("CassandraSearch", "Search test")
        res = self.db.search_notes("CassandraSearch")
        self.assertTrue(any(n["title"] == "CassandraSearch" for n in res))

    def test_stats(self):
        self.db.add_note("CassandraS1", "Stats", due_at=datetime.now().isoformat())
        self.db.add_note("CassandraS2", "Stats")
        stats = self.db.get_stats()
        self.assertGreaterEqual(stats["total_notes"], 2)

    def test_reminders(self):
        due_time = (datetime.now() + timedelta(seconds=10)).isoformat()
        self.db.add_note("CassandraRemind", "remind", due_at=due_time)
        reminders = self.db.get_upcoming_reminders(1)
        self.assertTrue(any(n["title"] == "CassandraRemind" for n in reminders))


class LoadBenchmarkTest(unittest.TestCase):
    def benchmark(self, cls, label):
        logger.info(f"[BENCH] {label}")
        if cls == NotesDatabaseMongo:
            db = NotesDatabaseMongo()
        elif cls == NotesDatabaseNeo4j:
            db = NotesDatabaseNeo4j()
        elif cls == NotesDatabasePostgreSQL:
            db = NotesDatabasePostgreSQL()
        elif cls == NotesDatabaseCassandra:
            db = NotesDatabaseCassandra()
        else:
            db = cls()

        count = 1000
        start_time = time.perf_counter()
        for i in range(count):
            db.add_note(f"T{i}", f"C {i}", due_at=None)
        elapsed = time.perf_counter() - start_time
        logger.info(f"Inserted {count} notes in {elapsed:.2f}s with {label}")
        self.assertTrue(elapsed < 10)

    def test_progress_load(self):
        self.benchmark(NotesDatabaseProgress, "Progress DB")

    @unittest.skipUnless(MONGO_AVAILABLE, "PyMongo not installed")
    def test_mongo_load(self):
        self.benchmark(NotesDatabaseMongo, "MongoDB")

    @unittest.skipUnless(NEO4J_AVAILABLE, "Neo4j driver not installed")
    def test_neo4j_load(self):
        self.benchmark(NotesDatabaseNeo4j, "Neo4j")

    @unittest.skipUnless(POSTGRESQL_AVAILABLE, "PostgreSQL driver not installed")
    def test_postgresql_load(self):
        self.benchmark(NotesDatabasePostgreSQL, "PostgreSQL")

    @unittest.skipUnless(CASSANDRA_AVAILABLE, "Cassandra driver not installed")
    def test_cassandra_load(self):
        self.benchmark(NotesDatabaseCassandra, "Cassandra")


if __name__ == "__main__":
    logger.info("Launching Notes DB backend tests...")
    unittest.main(verbosity=2)
