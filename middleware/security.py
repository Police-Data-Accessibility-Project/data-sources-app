import functools
from hmac import compare_digest
from flask import request, jsonify
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection
from datetime import datetime as dt
import os


def is_valid(api_key):
    psycopg2_connection = initialize_psycopg2_connection()
    # Get the user data that matches the API key from the request
    cursor = psycopg2_connection.cursor()
    cursor.execute(f"select id, api_key from users where api_key = '{api_key}'")
    results = cursor.fetchall()
    user_data = {}
    if not results:
        cursor.execute(
            f"delete from access_tokens where expiration_date < '{dt.now()}'"
        )
        psycopg2_connection.commit()
        cursor.execute(f"select id, token from access_tokens where token = '{api_key}'")
        results = cursor.fetchall()

        if not results:
            return False

    user_data = dict(zip(("id", "api_key"), results[0]))
    # Compare the API key in the user table to the API in the request header and proceed through the protected route if it's valid. Otherwise, compare_digest will return False and api_required will send an error message to provide a valid API key
    if compare_digest(user_data.get("api_key"), api_key):
        return True


# The api_required decorator can be added to protect a route so that only authenticated users can access the information
# To protect a route with this decorator, add @api_required on the line above a given route
# The request header for a protected route must include an "Authorization" key with the value formatted as "Bearer [api_key]"
# A user can get an API key by signing up and logging in (see User.py)
def api_required(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        api_key = None
        if request.headers and "Authorization" in request.headers:
            authorization_header = request.headers["Authorization"].split(" ")
            if len(authorization_header) >= 2 and authorization_header[0] == "Bearer":
                api_key = request.headers["Authorization"].split(" ")[1]
                if api_key == "undefined":
                    return {"message": "Please provide an API key"}, 400
            else:
                return {
                    "message": "Please provide a properly formatted bearer token and API key"
                }, 400
        else:
            return {
                "message": "Please provide an 'Authorization' key in the request header"
            }, 400
        # Check if API key is correct and valid
        if is_valid(api_key):
            return func(*args, **kwargs)
        else:
            return {"message": "The provided API key is not valid"}, 403

    return decorator
