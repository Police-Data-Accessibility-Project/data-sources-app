import functools
from hmac import compare_digest
from flask import request, jsonify
from middleware.initialize_supabase_client import initialize_supabase_client

def is_valid(access_token):
    supabase = initialize_supabase_client()
    user = supabase.table('users').select("*").eq('access_token', access_token).execute()
    user_data = user.get('data', [])
    print(user) 
    if compare_digest(user_data.access_token, access_token):
        return True

def api_required(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        if request.headers:
          access_token = request.headers['Authorization'].split(" ")[1]
        else:
            return {"message": "Please provide an API key"}, 400
        # Check if API key is correct and valid
        if is_valid(access_token):
            return func(*args, **kwargs)
        else:
            return {"message": "The provided API key is not valid"}, 403
    return decorator