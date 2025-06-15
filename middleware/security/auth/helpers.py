from typing import Optional

from werkzeug.exceptions import BadRequest, Unauthorized

from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.header.helpers import get_header_auth_info
from middleware.security.auth.method_config.core import AuthMethodConfig
from middleware.security.auth.method_config.enums import AuthScheme
from middleware.security.auth.method_config.map import AUTH_METHODS_MAP


def get_authentication(
    allowed_access_methods: list[AccessTypeEnum],
    restrict_to_permissions: Optional[list[PermissionsEnum]] = None,
    no_auth: bool = False,
) -> Optional[AccessInfoPrimary]:
    """
    Authenticate the user based on allowed access methods and optionally restrict permissions.

    :param allowed_access_methods: List of allowed access methods (API_KEY, JWT).
    :param restrict_to_permissions: Optional list of permissions to restrict the access.
    :return: AccessInfo object containing user email and access type.
    :raises HTTPException: If authentication fails.
    """
    if no_auth:
        return None

    hai = get_header_auth_info()

    check_if_valid_auth_scheme(hai.auth_scheme, allowed_access_methods)

    for access_method in allowed_access_methods:
        amc: AuthMethodConfig = AUTH_METHODS_MAP.get(access_method)
        if amc is None:
            continue

        access_info = try_authentication(
            allowed_access_methods=allowed_access_methods,
            access_type=access_method,
            handler=amc.handler,
            token=hai.token,
            restrict_to_permissions=restrict_to_permissions,
        )
        if access_info:
            return access_info

    raise Unauthorized(get_authentication_error_message(allowed_access_methods))


def check_if_valid_auth_scheme(
    auth_scheme: AuthScheme, allowed_access_methods: list[AccessTypeEnum]
):
    for access_method in allowed_access_methods:
        amc: AuthMethodConfig = AUTH_METHODS_MAP.get(access_method)
        if auth_scheme == amc.scheme:
            return

    raise BadRequest("Invalid Auth Scheme for endpoint")


def try_authentication(
    allowed_access_methods: list[AccessTypeEnum],
    access_type: AccessTypeEnum,
    handler: callable,
    **kwargs,
):
    """
    Generalized function to attempt authentication using a specific handler.

    :param allowed_access_methods: List of allowed access methods.
    :param access_type: The type of access being authenticated (e.g., JWT, API_KEY).
    :param handler: A callable that handles the specific authentication logic.
    :return: AccessInfo or None if authentication fails.
    """
    if access_type in allowed_access_methods:
        return handler(**kwargs)
    return None


def get_authentication_error_message(
    allowed_access_methods: list[AccessTypeEnum],
) -> str:
    f"""
    Please provide a valid form of one of the following: {[access_method.value for access_method in allowed_access_methods]} 
    """
