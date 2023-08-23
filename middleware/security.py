import functools
from hmac import compare_digest
from flask import request, jsonify
from middleware.initialize_supabase_client import initialize_supabase_client

def is_valid(api_key):
    supabase = initialize_supabase_client()
    user = supabase.table('users').select("*").eq('api_key', api_key).execute()
    user_data = {}
    if user:
        if len(user.data) > 0:
            user_data = user.data[0]
    if compare_digest(user_data['api_key'], api_key):
        return True

def api_required(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        api_key = None
        if request.headers and 'Authorization' in request.headers:
            api_key = request.headers['Authorization'].split(" ")[1]
            if api_key == "undefined":
                return {"message": "Please provide an API key"}, 400
        else:
            return {"message": "Please provide an API key"}, 400
        # Check if API key is correct and valid
        if is_valid(api_key):
            return func(*args, **kwargs)
        else:
            return {"message": "The provided API key is not valid"}, 403
    return decorator