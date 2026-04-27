import sqlite3
from pathlib import Path
from typing import Iterable

from .models import Memory, User, Visibility
from .policy import can_read_memory

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "demo.sqlite"


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT NOT NULL,
            team_id TEXT NOT NULL,
            owner_id TEXT NOT NULL,
            visibility TEXT NOT NULL,
            text TEXT NOT NULL,
            source TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (tenant_id, team_id, visibility, text)
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor_id TEXT NOT NULL,
            action TEXT NOT NULL,
            target TEXT NOT NULL,
            detail TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()


def add_memory(
    conn: sqlite3.Connection,
    user: User,
    team_id: str,
    text: str,
    visibility: Visibility = "team",
    source: str = "agent_writeback",
) -> bool:
    try:
        conn.execute(
            """
            INSERT INTO memories (tenant_id, team_id, owner_id, visibility, text, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user.tenant_id, team_id, user.user_id, visibility, text, source),
        )
        conn.execute(
            "INSERT INTO audit_log (actor_id, action, target, detail) VALUES (?, ?, ?, ?)",
            (user.user_id, "memory.create", f"{user.tenant_id}/{team_id}", text[:240]),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def seed_memory(conn: sqlite3.Connection, rows: Iterable[tuple[str, str, str, str, str]]) -> None:
    for owner_id, tenant_id, team_id, visibility, text in rows:
        conn.execute(
            """
            INSERT OR IGNORE INTO memories (tenant_id, team_id, owner_id, visibility, text, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (tenant_id, team_id, owner_id, visibility, text, "seed"),
        )
    conn.commit()


def search_memories(conn: sqlite3.Connection, user: User, query: str, limit: int = 5) -> list[Memory]:
    terms = [term.lower() for term in query.split() if len(term) >= 3]
    rows = conn.execute("SELECT * FROM memories WHERE tenant_id = ?", (user.tenant_id,)).fetchall()
    matches: list[tuple[int, Memory]] = []

    for row in rows:
        memory = Memory(
            id=row["id"],
            tenant_id=row["tenant_id"],
            team_id=row["team_id"],
            owner_id=row["owner_id"],
            visibility=row["visibility"],
            text=row["text"],
            source=row["source"],
        )
        if not can_read_memory(user, memory):
            continue
        text = memory.text.lower()
        score = sum(1 for term in terms if term in text)
        if score:
            matches.append((score, memory))

    matches.sort(key=lambda item: item[0], reverse=True)
    return [memory for _, memory in matches[:limit]]

