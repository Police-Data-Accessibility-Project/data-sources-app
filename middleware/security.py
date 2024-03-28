import functools
from hmac import compare_digest
from flask import request, jsonify
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection
from datetime import datetime as dt
from middleware.login_queries import is_admin
import os
from typing import Tuple
from flask.wrappers import Response
from psycopg2.extensions import cursor as PgCursor


def is_valid(api_key: str, endpoint: str, method: str) -> Tuple[bool, bool]:
    """
    Validates the API key and checks if the user has the required role to access a specific endpoint.

    :param api_key: The API key provided by the user.
    :param endpoint: The endpoint the user is trying to access.
    :param method: The HTTP method of the request.
    :return: A tuple (isValid, isExpired) indicating whether the API key is valid and not expired.
    """
    if not api_key:
        return False, False

    psycopg2_connection = initialize_psycopg2_connection()
    cursor = psycopg2_connection.cursor()
    cursor.execute(f"select id, api_key, role from users where api_key = '{api_key}'")
    results = cursor.fetchall()
    if len(results) > 0:
        role = results[0][2]

    if not results:
        cursor.execute(
            f"select email, expiration_date from session_tokens where token = '{api_key}'"
        )
        results = cursor.fetchall()
        if len(results) > 0:
            email = results[0][0]
            expiration_date = results[0][1]
            print(expiration_date, dt.utcnow())

            if expiration_date < dt.utcnow():
                return False, True

            if is_admin(cursor, email):
                role = "admin"

    if not results:
        cursor.execute(f"select id, token from access_tokens where token = '{api_key}'")
        results = cursor.fetchall()
        cursor.execute(
            f"delete from access_tokens where expiration_date < '{dt.utcnow()}'"
        )
        psycopg2_connection.commit()
        role = "user"

        if not results:
            return False, False

    if endpoint in ("datasources", "datasourcebyid") and method in ("PUT", "POST"):
        if role != "admin":
            return False, False

    # Compare the API key in the user table to the API in the request header and proceed
    # through the protected route if it's valid. Otherwise, compare_digest will return False
    # and api_required will send an error message to provide a valid API key
    return True, False


def api_required(func):
    """
    The api_required decorator can be added to protect a route so that only authenticated users can access the information
    To protect a route with this decorator, add @api_required on the line above a given route
    The request header for a protected route must include an "Authorization" key with the value formatted as "Bearer [api_key]"
    A user can get an API key by signing up and logging in (see User.py)
    """

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
        valid, expired = is_valid(api_key, request.endpoint, request.method)
        if valid:
            return func(*args, **kwargs)
        else:
            if expired:
                return {"message": "The provided API key has expired"}, 401
            return {"message": "The provided API key is not valid"}, 403

    return decorator
