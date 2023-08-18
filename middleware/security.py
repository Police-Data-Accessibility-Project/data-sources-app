import functools
from hmac import compare_digest
from flask import request, jsonify
from middleware.initialize_supabase_client import initialize_supabase_client

def is_valid(api_key):
    supabase = initialize_supabase_client()
    user = supabase.table('users').select("*").eq('api_key', api_key).execute()
    user_data = user.get('data', [])
    if compare_digest(user_data.api_key, api_key):
        return True

def api_required(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        api_key = None
        if request.headers:
            api_key = request.headers['Authorization'].split(" ")[1]
        else:
            return {"message": "Please provide an API key"}, 400
        # Check if API key is correct and valid
        if is_valid(api_key):
            return func(*args, **kwargs)
        else:
            return {"message": "The provided API key is not valid"}, 403
    return decorator