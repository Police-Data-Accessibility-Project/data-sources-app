from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_jwt_extended import create_access_token
import uuid

class User(Resource):
    def __init__(self, **kwargs):
        self.supabase = kwargs['supabase']

    def get(self):        
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            user_data = self.supabase.table('users').select('*').eq('email', email).execute()['data']
            user = {}
            if len(user_data) > 0:
                user = user_data[0]
            else:
                return {'error': 'no match'}
            if check_password_hash(user['password_digest'], password):
                api_key = uuid.uuid4().hex
                user_id = str(user['id'])
                test = self.supabase.table('users').update({'api_key': api_key}).eq('id', user_id).execute()
                print(test)
                return jsonify({'api_key': api_key})
        except Exception as e:
            return {'error': str(e)}
    
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            password_digest = generate_password_hash(password)
            user = self.supabase.table('users').insert({"email": email, "password_digest": password_digest}).execute()
            return user
        except Exception as e:
            return {'error': e}
        
