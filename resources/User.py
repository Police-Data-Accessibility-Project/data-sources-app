from flask_restful import Resource
from flask import request
from flask_jwt import jwt_required
import jwt
import os

class User(Resource):
    def get(self):
        try:
            email = request.get_json('email')
            password = request.get_json('password')
            user = self.supabase.table('users').select('*').eq('email', email).execute()['data']
            SECRET_KEY = os.getenv('SECRET_KEY')
            if self.bcrypt.check_password_hash(user.password_digest, password):
                token = jwt.encode({'payload': user}, SECRET_KEY, algorithm="HS256")
                return token
        except Exception as e:
            return {'error': e}
    
    def post(self):
        try:
            email = request.get_json('email')
            password = request.get_json('password')
            password_digest = self.bcrypt.generate_password_hash(password)
            user = self.supabase.table('users').insert({email, password_digest}).execute()
            return user
        except Exception as e:
            return {'error': e}