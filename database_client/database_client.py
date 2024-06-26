from collections import namedtuple
from typing import Union, Optional

import psycopg2


class DatabaseClient:

    def __init__(self, cursor: psycopg2.extensions.cursor):
        self.cursor = cursor

    def add_new_user(self, email: str, password_digest: str):
        """
        Adds a new user to the database.
        :param email:
        :param password_digest:
        :return:
        """
        self.cursor.execute(
            f"insert into users (email, password_digest) values (%s, %s)",
            (email, password_digest),
        )

    def get_user_id(self, email: str) -> Optional[int]:
        """
        Gets the ID of a user in the database based on their email.
        :param email:
        :return:
        """
        self.cursor.execute(f"select id from users where email = %s", (email,))
        if self.cursor.rowcount == 0:
            return None
        return self.cursor.fetchone()[0]

    def set_user_password_digest(self, email: str, password_digest: str):
        """
        Updates the password digest for a user in the database.
        :param email:
        :param password_digest:
        :return:
        """
        self.cursor.execute(
            f"update users set password_digest = %s where email = %s",
            (password_digest, email),
        )

    ResetTokenInfo = namedtuple("ResetTokenInfo", ["id", "email", "create_date"])

    def get_reset_token_info(self, token: str) -> Optional[ResetTokenInfo]:
        """
        Checks if a reset token exists in the database and retrieves the associated user data.

        :param token: The reset token to check.
        :return: ResetTokenInfo if the token exists; otherwise, None.
        """
        self.cursor.execute(
            f"select id, email, create_date from reset_tokens where token = %s",
            (token,),
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        return self.ResetTokenInfo(
            id=row[0], email=row[1], create_date=row[2]
        )

    def add_reset_token(self, email: str, token: str):
        """
        Inserts a new reset token into the database for a specified email.

        :param email: The email to associate with the reset token.
        :param token: The reset token to add.
        """
        self.cursor.execute(
            f"insert into reset_tokens (email, token) values (%s, %s)", (email, token)
        )

    def delete_reset_token(self, email: str, token: str):
        """
        Deletes a reset token from the database for a specified email.

        :param email: The email associated with the reset token to delete.
        :param token: The reset token to delete.
        """
        self.cursor.execute(
            f"delete from reset_tokens where email = %s and token = %s", (email, token)
        )

    SessionTokenInfo = namedtuple("SessionTokenInfo", ["email", "expiration_date"])

    def get_session_token_info(self, api_key: str) -> Optional[SessionTokenInfo]:
        """
        Checks if a session token exists in the database and retrieves the associated user data.

        :param api_key: The session token to check.
        :return: SessionTokenInfo if the token exists; otherwise, None.
        """
        self.cursor.execute(
            f"select email, expiration_date from session_tokens where token = %s",
            (api_key,),
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        return self.SessionTokenInfo(
            email=row[0], expiration_date=row[1]
        )

    RoleInfo = namedtuple("RoleInfo", ["id", "role"])

    def get_role_by_api_key(self, api_key: str) -> Optional[RoleInfo]:
        """
        Get role and user id for a given api key
        :param api_key: The api key to check.
        :return: RoleInfo if the token exists; otherwise, None.
        """
        self.cursor.execute(
            f"select id, role from users where api_key = %s",
            (api_key,),
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        return self.RoleInfo(
            id=row[0], role=row[1]
        )

    def update_user_api_key(self, api_key: str, user_id: int):
        """
        Update the api key for a user
        :param api_key: The api key to check.
        :param user_id: The user id to update.
        """
        self.cursor.execute(
            f"update users set api_key = %s where id = %s",
            (api_key, user_id),
        )
