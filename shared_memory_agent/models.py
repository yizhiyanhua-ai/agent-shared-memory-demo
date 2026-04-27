from dataclasses import dataclass
from typing import Literal

Visibility = Literal["private", "team", "tenant"]


@dataclass(frozen=True)
class User:
    user_id: str
    tenant_id: str
    team_id: str
    roles: tuple[str, ...]
    allowed_sources: tuple[str, ...]


@dataclass(frozen=True)
class Memory:
    id: int
    tenant_id: str
    team_id: str
    owner_id: str
    visibility: Visibility
    text: str
    source: str


@dataclass(frozen=True)
class PrivateDocument:
    doc_id: str
    tenant_id: str
    source: str
    title: str
    body: str
    classification: str

