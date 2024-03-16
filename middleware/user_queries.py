from werkzeug.security import generate_password_hash
from psycopg2.extensions import cursor as PgCursor
from typing import Dict, Union

def user_check_email(cursor: PgCursor, email: str) -> Dict[str, Union[int, str]]:
    """
    Checks if a user exists in the database by email.

def user_check_email(cursor, email):
    cursor.execute(f"select id from users where email = '{email}'")
    Parameters:
    - cursor: Database cursor to execute the query.
    - email: Email address to check in the database.

    Returns:
    - A dictionary with user ID if the user exists, or an error message if no match is found.
    """
    cursor.execute(f"select id from users where email = '{email}'")
    results = cursor.fetchall()
    if len(results) > 0:
        user_data = {"id": results[0][0]}
        return user_data
    else:
        return {"error": "no match"}


def user_post_results(cursor: PgCursor, email: str, password: str) -> None:
    """
    Creates a new user in the database with the provided email and password.

    Parameters:
    - cursor: Database cursor to execute the query.
    - email: Email address for the new user.
    - password: Password for the new user. It will be hashed before storage.

    Returns:
    - None
    """
    password_digest = generate_password_hash(password)
    cursor.execute(
        f"insert into users (email, password_digest) values ('{email}', '{password_digest}')"
    )

    return
