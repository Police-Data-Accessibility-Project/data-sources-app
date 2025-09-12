from db.helpers import get_offset


def test_get_offset():
    # Send a page number to the DatabaseClient method
    # Confirm that the correct offset is returned
    assert get_offset(page=3) == 200
