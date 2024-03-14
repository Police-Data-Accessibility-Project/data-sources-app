from typing import Dict, Any
from psycopg2.extensions import cursor as PgCursor

def check_reset_token(cursor: PgCursor, token: str) -> Dict[str, Any]:
    """
    Checks for the existence of a reset token in the database and returns the associated user data if found.

    Parameters:
    - cursor: A database cursor object used to execute SQL commands.
    - token: The reset token to check in the database.

    Returns:
    - A dictionary with user data (id, create_date, email) if the token is found, else a dictionary indicating no match.
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
    Adds a reset token to the database for a given email.

    Parameters:
    - cursor: A database cursor object used to execute SQL commands.
    - email: The email to associate with the reset token.
    - token: The reset token to add to the database.

    Returns:
    - None
    """
    cursor.execute(
        f"insert into reset_tokens (email, token) values ('{email}', '{token}')"
    )

def delete_reset_token(cursor: PgCursor, email: str, token: str) -> None:
    """
    Deletes a reset token from the database for a given email.

    Parameters:
    - cursor: A database cursor object used to execute SQL commands.
    - email: The email associated with the reset token.
    - token: The reset token to delete from the database.

    Returns:
    - None
    """
    cursor.execute(
        f"delete from reset_tokens where email = '{email}' and token = '{token}'"
    )

    return
