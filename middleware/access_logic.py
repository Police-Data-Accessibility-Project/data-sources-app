from dataclasses import dataclass
from enum import Enum, auto

from flask import request

from middleware.enums import PermissionsEnum


class InvalidAPIKeyException(Exception):
    pass


class InvalidAuthorizationHeaderException(Exception):
    pass


class AccessTypeEnum(Enum):
    JWT = auto()
    API_KEY = auto()

@dataclass
class AccessInfo:
    """
    A dataclass providing information on how the endpoint was accessed
    """
    access_type: AccessTypeEnum
    permissions: list[PermissionsEnum] = None

def get_access_info_from_jwt_or_api_key() -> AccessInfo:
    pass

def get_authorization_header_from_request() -> str:
    headers = request.headers
    try:
        return headers["Authorization"]
    except (KeyError, TypeError):
        raise InvalidAuthorizationHeaderException

def get_api_key_from_authorization_header(authorization_header: str) -> str:
    try:
        authorization_header_parts = authorization_header.split(" ")
        if authorization_header_parts[0] != "Basic":
            raise InvalidAPIKeyException
        return authorization_header_parts[1]
    except (ValueError, IndexError, AttributeError):
        raise InvalidAPIKeyException
