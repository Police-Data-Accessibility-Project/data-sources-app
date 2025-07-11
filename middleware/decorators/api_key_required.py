from functools import wraps

from middleware.primary_resource_logic.api_key import check_api_key


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
