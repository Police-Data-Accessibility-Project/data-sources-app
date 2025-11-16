from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from werkzeug.exceptions import BadRequest, Unauthorized

from middleware.enums import PermissionsEnum
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.jwt.service import JWTService


def validate_token(token: str) -> AccessInfoPrimary:
    try:
        return JWTService.get_access_info(token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def check_access(token: str, permission: PermissionsEnum) -> AccessInfoPrimary:
    access_info: AccessInfoPrimary = validate_token(token)
    if not access_info.has_permission(permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )
    return access_info


def get_relevant_permissions(raw_permissions: list[str]) -> list[PermissionsEnum]:
    relevant_permissions = []
    for raw_permission in raw_permissions:
        try:
            permission = PermissionsEnum(raw_permission)
            relevant_permissions.append(permission)
        except ValueError:
            continue
    return relevant_permissions


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_source_collector_data_sources_access_info(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> AccessInfoPrimary:
    try:
        return check_access(token, PermissionsEnum.SOURCE_COLLECTOR_DATA_SOURCES)
    # Translate exceptions into FastAPI exceptions
    except BadRequest as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.description,
        )
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.description,
        )



def get_standard_access_info(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> AccessInfoPrimary:
    return validate_token(token)
