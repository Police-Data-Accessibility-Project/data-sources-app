"""Unit tests for SimpleJWT.decode error handling on malformed tokens."""

import pytest
from jwt import DecodeError

from middleware.security.jwt.core import SimpleJWT
from middleware.security.jwt.enums import JWTPurpose


@pytest.mark.parametrize(
    "malformed_token",
    [
        "not-a-jwt",  # no dots → PyJWT ValueError on rsplit, wrapped to DecodeError
        "only.two",  # 1 dot → DecodeError: Not enough segments
        "",  # empty
        "garbage.garbage.garbage",  # 3 segments but not a valid JWT header
    ],
)
def test_decode_malformed_token_raises_decode_error(malformed_token: str):
    """Malformed tokens must raise DecodeError — not leak a bare ValueError
    — so callers can handle a single exception type.
    """
    with pytest.raises(DecodeError):
        SimpleJWT.decode(
            malformed_token, expected_purpose=JWTPurpose.GITHUB_ACCESS_TOKEN
        )
