from datetime import UTC, datetime


def now() -> datetime:
    """Current time; a dependency so tests can fix it."""
    return datetime.now(UTC)
