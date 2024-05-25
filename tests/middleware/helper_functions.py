"""This module contains helper functions used by middleware pytests."""

import uuid
from collections import namedtuple
from typing import Optional

import psycopg2.extensions

TestTokenInsert = namedtuple("TestTokenInsert", ["id", "email", "token"])
TestUser = namedtuple("TestUser", ["id", "email", "password_hash"])


def insert_test_agencies_and_sources(cursor: psycopg2.extensions.cursor) -> None:
    """
    Insert test agencies and sources into database.

    :param cursor:
    :return:
    """
    cursor.execute(
        """
        INSERT INTO
        PUBLIC.DATA_SOURCES (
            airtable_uid,
            NAME,
            DESCRIPTION,
            RECORD_TYPE,
            SOURCE_URL,
            APPROVAL_STATUS,
            URL_STATUS
        )
        VALUES
        ('SOURCE_UID_1','Source 1','Description of src1',
            'Type A','http://src1.com','approved','available'),
        ('SOURCE_UID_2','Source 2','Description of src2',
            'Type B','http://src2.com','needs identification','available'),
        ('SOURCE_UID_3','Source 3', 'Description of src3',
            'Type C', 'http://src3.com', 'pending', 'available');

        INSERT INTO public.agencies
        (airtable_uid, name, municipality, state_iso,
            county_name, count_data_sources, lat, lng)
        VALUES 
            ('Agency_UID_1', 'Agency A', 'City A',
                'CA', 'County X', 3, 30, 20),
            ('Agency_UID_2', 'Agency B', 'City B',
                'NY', 'County Y', 2, 40, 50),
            ('Agency_UID_3', 'Agency C', 'City C',
                'TX', 'County Z', 1, 90, 60);

        INSERT INTO public.agency_source_link
        (airtable_uid, agency_described_linked_uid)
        VALUES
            ('SOURCE_UID_1', 'Agency_UID_1'),
            ('SOURCE_UID_2', 'Agency_UID_2'),
            ('SOURCE_UID_3', 'Agency_UID_3');
        """
    )


def get_reset_tokens_for_email(
    db_cursor: psycopg2.extensions.cursor, reset_token_insert: TestTokenInsert
) -> tuple:
    """
    Get all reset tokens associated with an email.

    :param db_cursor:
    :param reset_token_insert:
    :return:
    """
    db_cursor.execute(
        """
        SELECT email from RESET_TOKENS where email = %s
        """,
        (reset_token_insert.email,),
    )
    results = db_cursor.fetchall()
    return results


def create_reset_token(cursor: psycopg2.extensions.cursor) -> TestTokenInsert:
    """
    Create a test user and associated reset token.

    :param cursor:
    :return:
    """
    user = create_test_user(cursor)
    token = uuid.uuid4().hex
    cursor.execute(
        """
        INSERT INTO reset_tokens(email, token)
        VALUES (%s, %s)
        RETURNING id
        """,
        (user.email, token),
    )
    id = cursor.fetchone()[0]
    return TestTokenInsert(id=id, email=user.email, token=token)


def create_test_user(
    cursor,
    email="example@example.com",
    password_hash="hashed_password_here",
    api_key="api_key_here",
    role=None,
) -> TestUser:
    """
    Create test user and return the id of the test user.

    :param cursor:
    :return: user id
    """
    cursor.execute(
        """
        INSERT INTO users (email, password_digest, api_key, role)
        VALUES
        (%s, %s, %s, %s)
        RETURNING id;
        """,
        (email, password_hash, api_key, role),
    )
    return TestUser(
        id=cursor.fetchone()[0],
        email=email,
        password_hash=password_hash,
    )


QuickSearchQueryLogResult = namedtuple(
    "QuickSearchQueryLogResult", ["result_count", "updated_at", "results"]
)


def get_most_recent_quick_search_query_log(
    cursor: psycopg2.extensions.cursor, search: str, location: str
) -> Optional[QuickSearchQueryLogResult]:
    """
    Retrieve most recent quick search query log for a search and location.

    :param cursor: The Cursor object of the database connection.
    :param search: The search query string.
    :param location: The location string.
    :return: A QuickSearchQueryLogResult object
        containing the result count and updated timestamp.
    """
    cursor.execute(
        """
        SELECT RESULT_COUNT, CREATED_AT, RESULTS FROM QUICK_SEARCH_QUERY_LOGS WHERE
        search = %s AND location = %s ORDER BY CREATED_AT DESC LIMIT 1
        """,
        (search, location),
    )
    result = cursor.fetchone()
    if result is None:
        return result
    return QuickSearchQueryLogResult(
        result_count=result[0], updated_at=result[1], results=result[2]
    )


def has_expected_keys(result_keys: list, expected_keys: list) -> bool:
    """
    Check that given result includes expected keys.

    :param result:
    :param expected_keys:
    :return: True if has expected keys, false otherwise
    """
    return not set(expected_keys).difference(result_keys)


def get_boolean_dictionary(keys: tuple) -> dict:
    """
    Creates dictionary of booleans, all set to false.

    :param keys:
    :return: dictionary of booleans
    """
    d = {}
    for key in keys:
        d[key] = False
    return d
