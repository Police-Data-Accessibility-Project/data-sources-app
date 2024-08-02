from functools import wraps

from flask import redirect, url_for, make_response, session

from database_client.database_client import DatabaseClient
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth_authorize"))
        return f(*args, **kwargs)

    return decorated_function


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("authorize"))

            psycopg2_connection = initialize_psycopg2_connection()
            db_client = DatabaseClient(psycopg2_connection.cursor())
            user_id = session["user_id"]
            user_permissions = db_client.get_user_permissions(user_id)
            if user_permissions is None:
                return (
                    make_response(
                        {"error": "You do not have permission to access this resource."}
                    ),
                    403,
                )
            if user_permissions.get(permission):
                return f(*args, **kwargs)

        return decorated_function

    return decorator
