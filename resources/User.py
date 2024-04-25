from werkzeug.security import generate_password_hash
from flask import request
from middleware.user_queries import user_post_results
from middleware.security import api_required
from typing import Dict, Any

from resources.PsycopgResource import PsycopgResource


class User(PsycopgResource):
    """
    A resource for user management, allowing new users to sign up and existing users to update their passwords.
    """

    def post(self) -> Dict[str, Any]:
        """
        Allows a new user to sign up by providing an email and password.

        The email and a hashed password are stored in the database. Upon successful registration,
        a message is returned to the user.

        Returns:
        - A dictionary containing a success message or an error message if the operation fails.
        """
        try:
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
            cursor = self.psycopg2_connection.cursor()
            user_post_results(cursor, email, password)
            self.psycopg2_connection.commit()

            return {"message": "Successfully added user"}

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": e}, 500

    # Endpoint for updating a user's password
    @api_required
    def put(self) -> Dict[str, Any]:
        """
        Allows an existing user to update their password.

        The user's new password is hashed and updated in the database based on their email.
        Upon successful password update, a message is returned to the user.

        Returns:
        - A dictionary containing a success message or an error message if the operation fails.
        """
        try:
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
            password_digest = generate_password_hash(password)
            cursor = self.psycopg2_connection.cursor()
            cursor.execute(
                f"update users set password_digest = '{password_digest}' where email = '{email}'"
            )
            self.psycopg2_connection.commit()
            return {"message": "Successfully updated password"}

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": e}, 500
            return {"message": e}, 500
