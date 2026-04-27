from .models import Memory, PrivateDocument, User


USERS: dict[str, User] = {
    "alice": User(
        user_id="alice",
        tenant_id="acme-corp",
        team_id="product",
        roles=("product_manager",),
        allowed_sources=("public", "product"),
    ),
    "bob": User(
        user_id="bob",
        tenant_id="acme-corp",
        team_id="finance",
        roles=("finance_analyst",),
        allowed_sources=("public", "finance"),
    ),
    "cara": User(
        user_id="cara",
        tenant_id="acme-corp",
        team_id="support",
        roles=("support_lead",),
        allowed_sources=("public", "support"),
    ),
}


def get_user(user_id: str) -> User:
    try:
        return USERS[user_id]
    except KeyError as exc:
        raise ValueError(f"Unknown user: {user_id}") from exc


def can_read_memory(user: User, memory: Memory) -> bool:
    if user.tenant_id != memory.tenant_id:
        return False
    if memory.visibility == "tenant":
        return True
    if memory.visibility == "team":
        return user.team_id == memory.team_id
    return user.user_id == memory.owner_id


def can_write_team_memory(user: User, team_id: str) -> bool:
    return user.team_id == team_id


def can_read_document(user: User, doc: PrivateDocument) -> bool:
    return user.tenant_id == doc.tenant_id and doc.source in user.allowed_sources

