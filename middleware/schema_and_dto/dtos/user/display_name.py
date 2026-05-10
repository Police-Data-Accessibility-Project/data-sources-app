"""
Shared validator and field constants for the user `display_name` property.

A user's display name is a public, case-insensitive-unique handle composed of
letters, numbers, hyphens, and underscores. See issue #875 for context.
"""

import re

DISPLAY_NAME_MIN_LENGTH = 3
DISPLAY_NAME_MAX_LENGTH = 30
DISPLAY_NAME_PATTERN = r"^[A-Za-z0-9_-]+$"
_DISPLAY_NAME_REGEX = re.compile(DISPLAY_NAME_PATTERN)

DISPLAY_NAME_LENGTH_MESSAGE = (
    f"display_name must be between {DISPLAY_NAME_MIN_LENGTH} "
    f"and {DISPLAY_NAME_MAX_LENGTH} characters."
)
DISPLAY_NAME_CHARSET_MESSAGE = (
    "display_name may only contain letters, numbers, hyphens, and underscores "
    "(no spaces or other punctuation)."
)
DISPLAY_NAME_DUPLICATE_MESSAGE = (
    "display_name is already taken (matches are case-insensitive)."
)


def validate_display_name(value: str) -> str:
    """Validate display_name length and character set, returning the value.

    Raises ``ValueError`` so it can be used inside Pydantic field validators —
    Pydantic wraps ``ValueError`` into a ``ValidationError`` with the message
    intact.
    """
    if not isinstance(value, str):
        raise ValueError(DISPLAY_NAME_CHARSET_MESSAGE)
    if (
        len(value) < DISPLAY_NAME_MIN_LENGTH
        or len(value) > DISPLAY_NAME_MAX_LENGTH
    ):
        raise ValueError(DISPLAY_NAME_LENGTH_MESSAGE)
    if not _DISPLAY_NAME_REGEX.fullmatch(value):
        raise ValueError(DISPLAY_NAME_CHARSET_MESSAGE)
    return value


def default_display_name_for_user_id(user_id: int) -> str:
    """Return the default display_name to assign when none is provided.

    Defaults to the numeric user id as a string, left-padded with zeros to
    satisfy the minimum length validator (e.g. user 7 -> "007").
    """
    return str(user_id).rjust(DISPLAY_NAME_MIN_LENGTH, "0")
