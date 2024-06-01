import datetime
import uuid

import pytest
from unittest.mock import patch

from middleware.login_queries import create_session_token
from middleware.security import is_valid, APIKeyStatus
from tests.helper_functions import (
    create_test_user,
    UserInfo,
    give_user_admin_role,
    create_api_key_db,
)
from tests.fixtures import dev_db_connection


def test_no_api_key_provided():
    result = is_valid(api_key="", endpoint="", method="")
    assert result == APIKeyStatus(is_valid=False, is_expired=False)


def test_api_key_exists_in_users_table_with_admin_role(dev_db_connection):
    cursor = dev_db_connection.cursor()
    test_user = create_test_user(cursor)
    give_user_admin_role(dev_db_connection, UserInfo(test_user.email, ""))
    api_key = create_api_key_db(cursor, test_user.id)
    dev_db_connection.commit()
    result = is_valid(api_key, "", "")
    assert result == APIKeyStatus(is_valid=True, is_expired=False)


def test_api_key_exists_in_users_table_with_non_admin_role(dev_db_connection):
    cursor = dev_db_connection.cursor()
    test_user = create_test_user(cursor)
    api_key = create_api_key_db(cursor, test_user.id)
    dev_db_connection.commit()
    result = is_valid(api_key, "", "")
    assert result == APIKeyStatus(is_valid=True, is_expired=False)


def test_api_key_not_in_users_table_but_in_session_tokens_table(dev_db_connection):
    cursor = dev_db_connection.cursor()
    test_user = create_test_user(cursor)
    token = create_session_token(cursor, test_user.id, test_user.email)
    dev_db_connection.commit()
    result = is_valid(token, "", "")
    assert result == APIKeyStatus(is_valid=True, is_expired=False)


def test_expired_session_token(dev_db_connection):
    cursor = dev_db_connection.cursor()
    test_user = create_test_user(cursor)
    token = create_session_token(cursor, test_user.id, test_user.email)
    cursor.execute(
        f"UPDATE session_tokens SET expiration_date = '{datetime.date(year=2020, month=3, day=4)}' WHERE token = '{token}'"
    )
    dev_db_connection.commit()
    result = is_valid(token, "", "")
    assert result == APIKeyStatus(is_valid=False, is_expired=True)


def test_session_token_with_admin_role(dev_db_connection):
    cursor = dev_db_connection.cursor()
    test_user = create_test_user(cursor)
    give_user_admin_role(dev_db_connection, UserInfo(test_user.email, ""))
    token = create_session_token(cursor, test_user.id, test_user.email)
    dev_db_connection.commit()
    result = is_valid(token, "", "")
    assert result == APIKeyStatus(is_valid=True, is_expired=False)


def test_api_key_exists_in_access_tokens_table(dev_db_connection):
    cursor = dev_db_connection.cursor()
    token = uuid.uuid4().hex
    expiration = datetime.datetime(year=2030, month=1, day=1)
    cursor.execute(
        f"insert into access_tokens (token, expiration_date) values (%s, %s)",
        (token, expiration),
    )
    dev_db_connection.commit()
    result = is_valid(token, "", "")
    assert result == APIKeyStatus(is_valid=True, is_expired=False)


def test_api_key_not_exist_in_any_table(dev_db_connection):
    token = uuid.uuid4().hex
    result = is_valid(token, "", "")
    assert result == APIKeyStatus(is_valid=False, is_expired=False)


def test_expired_access_token_in_access_tokens_table(dev_db_connection):
    cursor = dev_db_connection.cursor()
    token = uuid.uuid4().hex
    expiration = datetime.datetime(year=1999, month=1, day=1)
    cursor.execute(
        f"insert into access_tokens (token, expiration_date) values (%s, %s)",
        (token, expiration),
    )
    dev_db_connection.commit()
    result = is_valid(token, "", "")
    assert result == APIKeyStatus(is_valid=False, is_expired=False)


def test_admin_only_action_with_non_admin_role(dev_db_connection):
    cursor = dev_db_connection.cursor()
    test_user = create_test_user(cursor)
    api_key = create_api_key_db(cursor, test_user.id)
    dev_db_connection.commit()
    result = is_valid(api_key, "datasources", "PUT")
    assert result == APIKeyStatus(is_valid=False, is_expired=False)


def test_admin_only_action_with_admin_role(dev_db_connection):
    cursor = dev_db_connection.cursor()
    test_user = create_test_user(cursor)
    give_user_admin_role(dev_db_connection, UserInfo(test_user.email, ""))
    api_key = create_api_key_db(cursor, test_user.id)
    dev_db_connection.commit()
    result = is_valid(api_key, "datasources", "PUT")
    assert result == APIKeyStatus(is_valid=True, is_expired=False)

