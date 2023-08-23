from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from flask import request, jsonify
import uuid

class User(Resource):
    def __init__(self, **kwargs):
        self.supabase = kwargs['supabase']

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
            user_data = {}
            if user:
                if len(user.data) > 0:
                    user_data = user.data[0]
            return user_data
        except Exception as e:
            return {'error': e}
        
