import sqlite3
from datetime import datetime
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts (
  phone TEXT PRIMARY KEY,
  display_name TEXT,
  tier TEXT NOT NULL,
  notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS memories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  phone TEXT NOT NULL,
  direction TEXT NOT NULL,
  text TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS commitments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  starts_at TEXT NOT NULL,
  priority INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'scheduled'
);
"""


class MemoryStore:
    def __init__(self, db_path: str) -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(SCHEMA)

    def upsert_contact(self, phone: str, tier: str, display_name: str = "", notes: str = "") -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO contacts(phone, display_name, tier, notes) VALUES(?, ?, ?, ?)
                ON CONFLICT(phone) DO UPDATE SET display_name=excluded.display_name, tier=excluded.tier, notes=excluded.notes
                """,
                (phone, display_name, tier, notes),
            )

    def get_contact(self, phone: str) -> tuple[str, str, str] | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT display_name, tier, notes FROM contacts WHERE phone = ?", (phone,)
            ).fetchone()
        return row if row else None

    def remember_message(self, phone: str, direction: str, text: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO memories(phone, direction, text, created_at) VALUES(?, ?, ?, ?)",
                (phone, direction, text, datetime.utcnow().isoformat()),
            )

    def recent_thread(self, phone: str, limit: int = 8) -> list[tuple[str, str]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT direction, text FROM memories WHERE phone = ? ORDER BY id DESC LIMIT ?",
                (phone, limit),
            ).fetchall()
        return list(reversed(rows))

    def add_commitment(self, title: str, starts_at: str, priority: int) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO commitments(title, starts_at, priority) VALUES(?, ?, ?)",
                (title, starts_at, priority),
            )

    def upcoming_commitments(self) -> list[tuple[str, str, int]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT title, starts_at, priority FROM commitments WHERE status='scheduled' ORDER BY starts_at ASC"
            ).fetchall()
        return rows
