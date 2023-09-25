from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from flask import request, jsonify
import uuid
import os
import jwt

class User(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs['psycopg2_connection']

    # Login function: allows a user to login using their email and password as credentials
    # The password is compared to the hashed password stored in the users table
    # Once the password is verified, an API key is generated, which is stored in the users table and sent to the verified user
    def get(self):        
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            cursor = self.psycopg2_connection.cursor()
            cursor.execute(f"select * from users where email = '{email}'")
            results = cursor.fetchall()
            user_data = {}
            if len(results) > 0:
                user_data = results[0]
            else:
                return {'error': 'no match'}
            if check_password_hash(user_data['password_digest'], password):
                api_key = uuid.uuid4().hex
                user_id = str(user_data['id'])
                cursor.execute(f"update users set api_key = {api_key} where id = {user_id}")
                payload = {'api_key': api_key}
                token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')
                return jsonify(token)
        except Exception as e:
            return {'error': str(e)}
    
    # Sign up function: allows a user to sign up by submitting an email and password. The email and a hashed password are stored in the users table and this data is returned to the user upon completion
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            password_digest = generate_password_hash(password)
            cursor = self.psycopg2_connection.cursor()
            cursor.execute(f"insert into users (email, password_digest) values (%s, %s)", (email, password_digest))
            #user = self.supabase.table('users').insert({"email": email, "password_digest": password_digest}).execute()
            self.psycopg2_connection.commit()

            return {"data": "Successfully added user"}

        except Exception as e:
            return {'error': e}
        
