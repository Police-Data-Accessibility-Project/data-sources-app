from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from flask import request, jsonify
import uuid
import os
import jwt

class User(Resource):
    def __init__(self, **kwargs):
        self.supabase = kwargs['supabase']

    # Login function: allows a user to login using their email and password as credentials
    # The password is compared to the hashed password stored in the users table
    # Once the password is verified, an API key is generated, which is stored in the users table and sent to the verified user
    def get(self):        
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            user = self.supabase.table('users').select('*').eq('email', email).execute()
            user_data = {}
            if user:
                if len(user.data) > 0:
                    user_data = user.data[0]
            else:
                return {'error': 'no match'}
            if check_password_hash(user_data['password_digest'], password):
                api_key = uuid.uuid4().hex
                user_id = str(user_data['id'])
                self.supabase.table('users').update({'api_key': api_key}).eq('id', user_id).execute()
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
            user = self.supabase.table('users').insert({"email": email, "password_digest": password_digest}).execute()
            user_data = {}
            if user:
                if len(user.data) > 0:
                    user_data = user.data[0]
            return user_data
        except Exception as e:
            return {'error': e}
        
