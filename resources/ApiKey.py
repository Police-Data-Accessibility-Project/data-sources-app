from werkzeug.security import check_password_hash
from flask import request
from middleware.login_queries import login_results
import uuid
from typing import Dict, Any, Optional

from resources.PsycopgResource import PsycopgResource, handle_exceptions


class ApiKey(PsycopgResource):
    """Represents a resource for generating an API key for authenticated users."""

    @handle_exceptions
    def get(self) -> Optional[Dict[str, Any]]:
        """
        Authenticates a user based on provided credentials and generates an API key.

        Reads the 'email' and 'password' from the JSON body of the request, validates the user,
        and if successful, generates and returns a new API key.

        Returns:
        - dict: A dictionary containing the generated API key, or None if an error occurs.
        """
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        cursor = self.psycopg2_connection.cursor()
        user_data = login_results(cursor, email)

        if check_password_hash(user_data["password_digest"], password):
            api_key = uuid.uuid4().hex
            user_id = str(user_data["id"])
            cursor.execute(
                "UPDATE users SET api_key = %s WHERE id = %s", (api_key, user_id)
            )
            payload = {"api_key": api_key}
            self.psycopg2_connection.commit()
            return payload
