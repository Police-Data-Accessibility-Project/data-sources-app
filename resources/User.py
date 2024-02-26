from werkzeug.security import generate_password_hash
from flask_restful import Resource
from flask import request
from middleware.user_queries import user_post_results
from middleware.security import api_required


class User(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

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

            return {"message": "Successfully added user"}

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": e}, 500

    # Endpoint for updating a user's password
    @api_required
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
            return {"message": "Successfully updated password"}

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": e}, 500
