import argparse

from .agent import answer
from .memory_store import add_memory, connect, init_db
from .policy import get_user
from .writeback import validate_writeback


def main() -> None:
    parser = argparse.ArgumentParser(description="Shared memory agent demo")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ask = subparsers.add_parser("ask", help="Ask with scoped memory and private-data retrieval")
    ask.add_argument("--user", required=True)
    ask.add_argument("--query", required=True)

    remember = subparsers.add_parser("remember", help="Write durable team memory with policy checks")
    remember.add_argument("--user", required=True)
    remember.add_argument("--team", required=True)
    remember.add_argument("--text", required=True)

    args = parser.parse_args()
    conn = connect()
    init_db(conn)
    user = get_user(args.user)

    if args.command == "ask":
        print(answer(conn, user, args.query))
        return

    allowed, reason = validate_writeback(user, args.team, args.text)
    if not allowed:
        print(f"Rejected write-back: {reason}")
        return

    created = add_memory(conn, user, args.team, args.text, visibility="team")
    if created:
        print(f"Stored team memory: {reason}")
    else:
        print("Skipped duplicate memory")


if __name__ == "__main__":
    main()

