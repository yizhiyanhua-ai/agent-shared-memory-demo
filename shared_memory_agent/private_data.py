from .models import PrivateDocument, User
from .policy import can_read_document


PRIVATE_DOCS = (
    PrivateDocument(
        doc_id="public-001",
        tenant_id="acme-corp",
        source="public",
        title="ACME onboarding overview",
        body="ACME onboarding requires workspace provisioning, SSO setup, and data residency review.",
        classification="internal",
    ),
    PrivateDocument(
        doc_id="product-042",
        tenant_id="acme-corp",
        source="product",
        title="ACME product rollout note",
        body="Product team decided that ACME beta rollout must verify EU data residency before enabling analytics export.",
        classification="confidential",
    ),
    PrivateDocument(
        doc_id="finance-017",
        tenant_id="acme-corp",
        source="finance",
        title="ACME renewal risk",
        body="Finance flagged ACME renewal as medium risk because invoice approval depends on procurement sign-off.",
        classification="restricted",
    ),
    PrivateDocument(
        doc_id="support-009",
        tenant_id="acme-corp",
        source="support",
        title="ACME support escalation",
        body="Support observed repeated SSO misconfiguration during ACME workspace onboarding.",
        classification="confidential",
    ),
)


def search_private_docs(user: User, query: str, limit: int = 5) -> list[PrivateDocument]:
    terms = [term.lower() for term in query.split() if len(term) >= 3]
    matches: list[tuple[int, PrivateDocument]] = []

    for doc in PRIVATE_DOCS:
        if not can_read_document(user, doc):
            continue
        haystack = f"{doc.title} {doc.body}".lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            matches.append((score, doc))

    matches.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in matches[:limit]]

