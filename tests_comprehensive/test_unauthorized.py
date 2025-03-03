import pytest

"""
All the tests in this file are expected to produce an UNAUTHORIZED response
"""


def test_unauthorized_jwt_expired():
    """
    All endpoints where a JWT (aka, "Bearer" auth) is listed as an option
    in the documentation should produce a BAD REQUEST result when a jwt is expired
    """
    pytest.fail("Not implemented")


def test_unauthorized_jwt_csrf():
    """
    All endpoints where a JWT (aka, "Bearer" auth) is listed as an option
    in the documentation should produce an UNAUTHORIZED result where the JWT
    in question is encrypted differently than the one present on the app
    """
    pytest.fail("Not implemented")


def test_unauthorized_api_key_not_allowed():
    """
    All endpoints where an API key is listed as an option
    in the documentation should produce an UNAUTHORIZED result an API key
    is not allowed
    """
    pytest.fail("Not implemented")
