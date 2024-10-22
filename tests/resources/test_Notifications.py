import pytest


def test_notifications_permissions():
    """
    Test that the notifications endpoint can only be called by someone
    with the `notifications` permission
    And is denied for any other user
    :return:
    """
    pytest.fail("Not implemented yet")