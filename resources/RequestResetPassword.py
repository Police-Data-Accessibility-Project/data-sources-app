from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from flask import request
from middleware.user_queries import user_check_email
from middleware.reset_token_queries import add_reset_token
import os
import uuid
import requests


class RequestResetPassword(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    def post(self):
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
