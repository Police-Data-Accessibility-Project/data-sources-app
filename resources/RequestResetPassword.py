from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from flask import request
from middleware.user_queries import user_check_email
from middleware.reset_token_queries import add_reset_token
import os
import uuid
import requests
from typing import Dict, Any


class RequestResetPassword(Resource):
    """
    Provides a resource for users to request a password reset. Generates a reset token
    and sends an email to the user with instructions on how to reset their password.
    """

    def __init__(self, **kwargs):
        """
        Initializes the RequestResetPassword resource with a database connection.

        Parameters:
        - kwargs (dict): Keyword arguments containing 'psycopg2_connection' for database connection.
        """
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    def post(self) -> Dict[str, Any]:
        """
        Processes a password reset request. Checks if the user's email exists in the database,
        generates a reset token, and sends an email with the reset link.

        Returns:
        - A dictionary containing a success message and the reset token, or an error message if an exception occurs.
        """
        try:
            data = request.get_json()
            email = data.get("email")
            cursor = self.psycopg2_connection.cursor()
            user_data = user_check_email(cursor, email)
            id = user_data["id"]
            token = uuid.uuid4().hex
            add_reset_token(cursor, email, token)
            self.psycopg2_connection.commit()

            body = f"To reset your password, click the following link: {os.getenv('VITE_VUE_APP_BASE_URL')}/reset-password/{token}"
            r = requests.post(
                "https://api.mailgun.net/v3/mail.pdap.io/messages",
                auth=("api", os.getenv("MAILGUN_KEY")),
                data={
                    "from": "mail@pdap.io",
                    "to": [email],
                    "subject": "PDAP Data Sources Reset Password",
                    "text": body,
                },
            )

            return {
                "message": "An email has been sent to your email address with a link to reset your password. It will be valid for 15 minutes.",
                "token": token,
            }

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"error": str(e)}, 500
