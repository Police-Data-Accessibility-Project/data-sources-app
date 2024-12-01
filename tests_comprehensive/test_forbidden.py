import pytest


def test_jwt_insufficient_permissions():
    """
    All endpoints where a JWT (aka, "Bearer" auth) is listed as an option
    in the documentation should produce a FORBIDDEN result where the JWT
    in question does not have the correct permissions
    """
    pytest.fail("Not implemented")
