from .memory_store import connect, init_db, seed_memory


def main() -> None:
    conn = connect()
    init_db(conn)
    seed_memory(
        conn,
        (
            ("alice", "acme-corp", "product", "team", "ACME onboarding always starts with workspace provisioning and EU data residency review."),
            ("bob", "acme-corp", "finance", "team", "Finance renewal reviews should include procurement sign-off status."),
            ("cara", "acme-corp", "support", "team", "Support should check SSO metadata before escalating ACME onboarding tickets."),
            ("alice", "acme-corp", "product", "tenant", "ACME is a strategic customer; keep handoffs explicit across teams."),
        ),
    )
    print("Seeded demo database at data/demo.sqlite")


if __name__ == "__main__":
    main()

