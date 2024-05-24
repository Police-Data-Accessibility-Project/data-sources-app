import uuid

import psycopg2.extensions
import pytest

from middleware.custom_exceptions import TokenNotFoundError
from middleware.reset_token_queries import (
    check_reset_token,
    add_reset_token,
    delete_reset_token,
)
from tests.middleware.helper_functions import (
    create_reset_token,
    create_test_user,
    get_reset_tokens_for_email,
)
from tests.middleware.fixtures import dev_db_connection, db_cursor


def test_check_reset_token(db_cursor: psycopg2.extensions.cursor) -> None:
    """
    Checks if a token existing in the database
    is properly returned by check_reset_token
    :param db_cursor:
    :return:
    """
    test_token_insert = create_reset_token(db_cursor)

    user_data = check_reset_token(db_cursor, test_token_insert.token)
    assert test_token_insert.id == user_data["id"]


def test_check_reset_token_raises_token_not_found_error(
    db_cursor: psycopg2.extensions,
) -> None:
    with pytest.raises(TokenNotFoundError):
        check_reset_token(db_cursor, token=str(uuid.uuid4()))


def test_add_reset_token(db_cursor: psycopg2.extensions.cursor) -> None:
    """
    Checks if add_reset_token properly inserts a token
    for the given email in the database
    """
    user = create_test_user(db_cursor)
    token = uuid.uuid4().hex
    add_reset_token(db_cursor, user.email, token)
    db_cursor.execute(
        """
        SELECT id, token FROM RESET_TOKENS where email = %s
        """,
        (user.email,),
    )
    results = db_cursor.fetchall()
    assert len(results) == 1
    assert results[0][1] == token


def test_delete_reset_token(db_cursor: psycopg2.extensions.cursor) -> None:
    """
    Checks if token previously inserted is deleted
    by the delete_reset_token method
    """
    reset_token_insert = create_reset_token(db_cursor)
    results = get_reset_tokens_for_email(db_cursor, reset_token_insert)
    assert len(results) == 1
    delete_reset_token(db_cursor, reset_token_insert.email, reset_token_insert.token)
    results = get_reset_tokens_for_email(db_cursor, reset_token_insert)
    assert len(results) == 0
