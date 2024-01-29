from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from flask import request
from middleware.user_queries import user_get_results, user_post_results


class User(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    def get(self):
        """
        Login function: allows a user to login using their email and password as credentials
        The password is compared to the hashed password stored in the users table
        Once the password is verified, an API key is generated, which is stored in the users table and sent to the verified user
        """
        try:
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
            cursor = self.psycopg2_connection.cursor()

            user_data = user_get_results(cursor, email)
            if check_password_hash(user_data["password_digest"], password):
                return {"data": "Successfully logged in"}

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"error": str(e)}

    def post(self):
        """
        Sign up function: allows a user to sign up by submitting an email and password.
        The email and a hashed password are stored in the users table and this data is returned to the user upon completion
        """
        try:
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
            cursor = self.psycopg2_connection.cursor()
            user_post_results(cursor, email, password)
            self.psycopg2_connection.commit()

            return {"data": "Successfully added user"}

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"error": e}

    # Endpoint for updating a user's password
    def put(self):
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
            return {"data": "Successfully updated password"}

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"error": e}
