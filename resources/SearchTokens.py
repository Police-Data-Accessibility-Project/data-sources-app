from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from flask import request, jsonify
import datetime
import uuid
import os
import jwt
import requests

class SearchTokens(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs['psycopg2_connection']

    # Login function: allows a user to login using their email and password as credentials
    # The password is compared to the hashed password stored in the users table
    # Once the password is verified, an API key is generated, which is stored in the users table and sent to the verified user
    def get(self, search, location):        
        try:
            if type(self.psycopg2_connection) == dict:
                return self.psycopg2_connection
            cursor = self.psycopg2_connection.cursor()
            token = uuid.uuid4().hex
            expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
            cursor.execute(f"insert into access_tokens (token, expiration_date) values (%s, %s)", (token, expiration))         
            self.psycopg2_connection.commit()

            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get(f"http://127.0.0.1:5001/quick-search/{search}/{location}", headers=headers)
            return r.json()

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {'error': e}
        
