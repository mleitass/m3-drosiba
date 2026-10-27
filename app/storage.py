"""Iesniegumu glabātuve: SQLite.

Lokāli datubāze ir fails iesniegumi.db (vides mainīgais EZERMALA_DB).
Ezerdati testa vidē datubāze ir Postgres (docker-compose.yml); šajā prototipā
tā nav pieslēgta. Testi izmanto datubāzi atmiņā (reset).
"""

import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone

from app import config

COLUMNS = (
    "id",
    "personalCode",
    "fullName",
    "email",
    "preferredChannel",
    "topic",
    "subject",
    "body",
    "status",
    "receivedAt",
    "dueDate",
    "replyChannel",
    "reasonCode",
    "department",
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS submissions (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT UNIQUE NOT NULL,
    personalCode TEXT NOT NULL,
    fullName TEXT NOT NULL,
    email TEXT NOT NULL,
    preferredChannel TEXT NOT NULL,
    topic TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT NOT NULL,
    receivedAt TEXT NOT NULL,
    dueDate TEXT NOT NULL,
    replyChannel TEXT NOT NULL,
    reasonCode TEXT,
    department TEXT
);
"""

# Sintētiski dati. Personas kodi neatbilst reālām personām.
SEED = (
    {
        "personalCode": "32000000101",
        "fullName": "Jānis Paraudziņš",
        "email": "janis.paraudzins@example.com",
        "preferredChannel": "EMAIL",
        "topic": "ROADS",
        "subject": "Bedre Ezera ielā",
        "body": "Ezera ielā pie 12. mājas ir dziļa bedre. Lūdzu, salabojiet to.",
        "status": "RECEIVED",
        "receivedAt": "2026-10-01T09:15:00+00:00",
        "dueDate": "2026-10-31",
        "replyChannel": "EMAIL",
        "reasonCode": None,
        "department": "UTILITIES",
    },
    {
        "personalCode": "32000000103",
        "fullName": "Ņikita Ezermalnieks",
        "email": "nikita.ezermalnieks@example.com",
        "preferredChannel": "E_ADDRESS",
        "topic": "HEATING_SUPPORT",
        "subject": "Apkures pabalsts",
        "body": "Lūdzu piešķirt apkures pabalstu šai sezonai.",
        "status": "IN_PROGRESS",
        "receivedAt": "2026-10-12T08:30:00+00:00",
        "dueDate": "2026-11-11",
        "replyChannel": "E_ADDRESS",
        "reasonCode": None,
        "department": "SOCIAL",
    },
)

_INSERT = f"""
    INSERT INTO submissions (seq, {", ".join(COLUMNS)})
    VALUES (?, {", ".join("?" for _ in COLUMNS)})
"""

_lock = threading.Lock()
_memory: sqlite3.Connection | None = None


def reset(seed: bool = True) -> None:
    """Testiem: tukša datubāze atmiņā, pēc izvēles ar sintētiskiem iesniegumiem."""
    global _memory
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    with _lock:
        _memory = conn
    if seed:
        for record in SEED:
            add(record)


@contextmanager
def _connection():
    with _lock:
        if _memory is not None:
            yield _memory
            _memory.commit()
            return
        conn = sqlite3.connect(config.DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.executescript(SCHEMA)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def add(data: dict) -> dict:
    with _connection() as conn:
        (seq,) = conn.execute(
            "SELECT COALESCE(MAX(seq), 0) + 1 FROM submissions"
        ).fetchone()
        record = {**data, "id": f"IES-2026-{seq:06d}"}
        conn.execute(_INSERT, [seq, *(record.get(column) for column in COLUMNS)])
    return record


def list_submissions(status: str | None = None, topic: str | None = None) -> list:
    # Parametrizēts vaicājums: ievade nekad nekļūst par SQL daļu.
    with _connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM submissions
            WHERE (:status IS NULL OR status = :status)
              AND (:topic IS NULL OR topic = :topic)
            ORDER BY seq
            """,
            {"status": status, "topic": topic},
        ).fetchall()
    return [{column: row[column] for column in COLUMNS} for row in rows]


def get(submission_id: str) -> dict | None:
    with _connection() as conn:
        row = conn.execute(
            "SELECT * FROM submissions WHERE id = ?", (submission_id,)
        ).fetchone()
    if row is None:
        return None
    return {column: row[column] for column in COLUMNS}


def now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def count() -> int:
    """Veselības pārbaudei: vai datubāzi var nolasīt."""
    with _connection() as conn:
        (total,) = conn.execute("SELECT COUNT(*) FROM submissions").fetchone()
    return total
