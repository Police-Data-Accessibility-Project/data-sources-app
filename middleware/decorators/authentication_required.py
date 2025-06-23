from functools import wraps
from typing import Optional, Callable

from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.security.auth.helpers import get_authentication


def authentication_required(
    allowed_access_methods: list[AccessTypeEnum],
    restrict_to_permissions: Optional[list[PermissionsEnum]] = None,
    no_auth: bool = False,
):
    """
    Checks if the user has access to the resource,
     and provides access info to the inner function

    Resource methods using this must include `access_info` in their kwargs.

    :param allowed_access_methods:
    :param restrict_to_permissions: Automatically abort if the user does not have the requisite permissions
    :return:
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs["access_info"] = get_authentication(
                allowed_access_methods, restrict_to_permissions, no_auth=no_auth
            )

            return func(*args, **kwargs)

        return wrapper

    return decorator
