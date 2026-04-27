from .models import User
from .policy import can_write_team_memory


WRITEBACK_SIGNALS = (
    "always",
    "decision",
    "standard",
    "policy",
    "runbook",
    "remember",
)

SENSITIVE_SIGNALS = (
    "password",
    "secret",
    "token",
    "api key",
    "salary",
)


def should_write_back(text: str) -> tuple[bool, str]:
    lowered = text.lower()
    if any(signal in lowered for signal in SENSITIVE_SIGNALS):
        return False, "blocked_sensitive_content"
    if any(signal in lowered for signal in WRITEBACK_SIGNALS):
        return True, "durable_team_knowledge"
    if len(text) < 40:
        return False, "too_short"
    return False, "missing_writeback_signal"


def validate_writeback(user: User, team_id: str, text: str) -> tuple[bool, str]:
    if not can_write_team_memory(user, team_id):
        return False, "wrong_team_scope"
    return should_write_back(text)

