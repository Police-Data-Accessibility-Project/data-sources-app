from contextlib import contextmanager
from typing import Iterator

import psycopg


@contextmanager
def managed_cursor(
    connection: psycopg.extensions.connection,
) -> Iterator[psycopg.extensions.cursor]:
    """
    Manage a cursor for a given database connection.

    :param connection: The psycopg database connection.
    :return: Iterator that yields the cursor
        and automatically commits changes on successful completion,
        or rolls back changes and closes the cursor on failure.
    """
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
