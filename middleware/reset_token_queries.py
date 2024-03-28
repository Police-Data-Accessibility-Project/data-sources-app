from psycopg2.extensions import cursor as PgCursor
from typing import Dict, Union


def check_reset_token(cursor: PgCursor, token: str) -> Dict[str, Union[int, str]]:
    """
    Checks if a reset token exists in the database and retrieves the associated user data.

    :param cursor: A cursor object from a psycopg2 connection.
    :param token: The reset token to check.
    :return: A dictionary containing the user's ID, token creation date, and email if the token exists; otherwise, an error message.
    """
    cursor.execute(
        f"select id, create_date, email from reset_tokens where token = '{token}'"
    )
    results = cursor.fetchall()
    if len(results) > 0:
        user_data = {
            "id": results[0][0],
            "create_date": results[0][1],
            "email": results[0][2],
        }
        return user_data
    else:
        return {"error": "no match"}


def add_reset_token(cursor: PgCursor, email: str, token: str) -> None:
    """
    Inserts a new reset token into the database for a specified email.

    :param cursor: A cursor object from a psycopg2 connection.
    :param email: The email to associate with the reset token.
    :param token: The reset token to add.
    """
    cursor.execute(
        f"insert into reset_tokens (email, token) values ('{email}', '{token}')"
    )

    return


def delete_reset_token(cursor: PgCursor, email: str, token: str) -> None:
    """
    Deletes a reset token from the database for a specified email.

    :param cursor: A cursor object from a psycopg2 connection.
    :param email: The email associated with the reset token to delete.
    :param token: The reset token to delete.
    """
    cursor.execute(
        f"delete from reset_tokens where email = '{email}' and token = '{token}'"
    )

    return
