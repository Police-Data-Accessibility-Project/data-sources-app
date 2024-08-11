import functools
from functools import wraps
from typing import Callable, Optional

from flask import redirect, url_for, session

from middleware.enums import PermissionsEnum
from middleware.security import check_api_key


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth_authorize"))
        return f(*args, **kwargs)

    return decorated_function



def api_key_required(permissions: Optional[PermissionsEnum] = None):
    """
    The api_key_required decorator can be added to protect a route so that only authenticated users can access the information.
    To protect a route with this decorator, add @api_key_required on the line above a given route.
    The request header for a protected route must include an "Authorization" key with the value formatted as "Basic [api_key]".
    A user can get an API key by signing up and logging in.
    """

    def decorator(func: Callable):

        @wraps(func)
        def wrapper(*args, **kwargs):
            check_api_key(permissions)
            return func(*args, **kwargs)

        return wrapper

    return decorator