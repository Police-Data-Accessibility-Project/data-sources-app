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

def check_decorator_factory(check_func: Callable[[Any], None], *args, **kwargs):
    """
    Factory function to create decorators that perform a check before executing the decorated function.
    check_func: The function that performs the check.
    *args, **kwargs: Additional arguments to be passed to the check_func.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*func_args, **func_kwargs):
            # Perform the check
            check_func(*args, **kwargs)
            # Call the decorated function
            return func(*func_args, **func_kwargs)

        return wrapper

    return decorator

# Example usage
api_key_required = check_decorator_factory(check_api_key)
permissions_required = lambda permissions: check_decorator_factory(check_permissions, permissions)
