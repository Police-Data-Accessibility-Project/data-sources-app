from flask_restful import Resource
from flask import request

class User(Resource):
    
    def post(self):
        try:
            email = request.get_json('email')
            password = request.get_json('password')
            password_digest = self.bcrypt.generate_password_hash(password)
            user = self.supabase.table('users').insert({email, password_digest}).execute()
            return user
        except Exception as e:
            return {'error': e}