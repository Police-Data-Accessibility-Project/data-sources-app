import functools
from functools import wraps
from typing import Callable, Optional, Any

from flask import redirect, url_for, session

from middleware.access_logic import get_access_info_from_jwt_or_api_key
from middleware.enums import PermissionsEnum
from middleware.security import check_api_key, check_permissions


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth_authorize"))
        return f(*args, **kwargs)

    return decorated_function


def api_key_or_jwt_required(f):
    def decorator(*args, **kwargs):

        @wraps(f)
        def wrapper(*args, **kwargs):
            kwargs["access_info"] = get_access_info_from_jwt_or_api_key()

            return f(*args, **kwargs)

        return wrapper(*args, **kwargs)

    return decorator


def api_key_required(func):
    """
    The api_key_required decorator can be added to protect a route so that only authenticated users can access the information.
    To protect a route with this decorator, add @api_key_required on the line above a given route.
    The request header for a protected route must include an "Authorization" key with the value formatted as "Basic [api_key]".
    A user can get an API key by signing up and logging in.
    """

    @wraps(func)
    def decorator(*args, **kwargs):
        check_api_key()
        return func(*args, **kwargs)

    return decorator


def permissions_required(permissions: PermissionsEnum):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            check_permissions(permissions)
            return func(*args, **kwargs)

        return wrapper

    return decorator
