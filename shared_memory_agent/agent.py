import sqlite3

from .memory_store import search_memories
from .models import User
from .private_data import search_private_docs


def answer(conn: sqlite3.Connection, user: User, query: str) -> str:
    memories = search_memories(conn, user, query)
    docs = search_private_docs(user, query)

    lines = [
        f"User: {user.user_id} ({user.team_id})",
        f"Query: {query}",
        "",
        "Accessible shared memories:",
    ]
    if memories:
        lines.extend(f"- [{memory.visibility}/{memory.team_id}] {memory.text}" for memory in memories)
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Accessible private data:")
    if docs:
        lines.extend(f"- [{doc.source}/{doc.classification}] {doc.title}: {doc.body}" for doc in docs)
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Agent response:")
    if memories or docs:
        lines.append("Use the retrieved facts above, keep source boundaries visible, and avoid writing back unless the content is durable team knowledge.")
    else:
        lines.append("No authorized context was found. Ask for a source or escalate to a user with the right permissions.")

    return "\n".join(lines)

