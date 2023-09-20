import functools
from hmac import compare_digest
from flask import request, jsonify
from middleware.initialize_supabase_client import initialize_supabase_client
import jwt
import os

def is_valid(api_key):
    supabase = initialize_supabase_client()
    # Get the user data that matches the API key from the request
    user = supabase.table('users').select("*").eq('api_key', api_key).execute()
    user_data = {}
    if user:
        if len(user.data) > 0:
            user_data = user.data[0]
        else:
            return False
    else:
        return False
    # Compare the API key in the user table to the API in the request header and proceed through the protected route if it's valid. Otherwise, compare_digest will return False and api_required will send an error message to provide a valid API key
    if compare_digest(user_data.get('api_key'), api_key):
        return True

# The api_required decorator can be added to protect a route so that only authenticated users can access the information
# To protect a route with this decorator, add @api_required on the line above a given route
# The request header for a protected route must include an "Authorization" key with the value formatted as "Bearer [api_key]"
# A user can get an API key by signing up and logging in (see User.py)
def api_required(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        api_key = None
        if request.headers and 'Authorization' in request.headers:
            authorization_header = request.headers['Authorization'].split(" ")
            if len(authorization_header) >= 2 and authorization_header[0] == "Bearer":
                try:
                    token = request.headers['Authorization'].split(" ")[1]
                    payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
                    api_key = payload['api_key']
                except jwt.InvalidTokenError:
                    return {"message": 'Invalid token.'}, 400
                if api_key == "undefined":
                    return {"message": "Please provide an API key"}, 400
            else:
                return {'message': "Please provide a properly formatted bearer token and API key"}, 400
        else:
            return {"message": "Please provide an 'Authorization' key in the request header"}, 400
        # Check if API key is correct and valid
        if is_valid(api_key):
            return func(*args, **kwargs)
        else:
            return {"message": "The provided API key is not valid"}, 403
    return decorator