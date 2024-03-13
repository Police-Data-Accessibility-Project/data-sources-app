from werkzeug.security import check_password_hash
from flask_restful import Resource
from flask import request
from middleware.login_queries import login_results
import uuid


class ApiKey(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    def get(self):
        """
        Generate an API key for a user that successfully logs in
        """
        try:
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

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": str(e)}
