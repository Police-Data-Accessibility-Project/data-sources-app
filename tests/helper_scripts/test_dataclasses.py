from dataclasses import dataclass
from typing import Optional

from flask.testing import FlaskClient

from database_client.database_client import DatabaseClient


@dataclass
class UserInfo:
    email: str
    password: str
    user_id: Optional[str] = None


@dataclass
class TestUserSetup:
    user_info: UserInfo
    api_key: str
    api_authorization_header: dict
    jwt_authorization_header: Optional[dict] = None


@dataclass
class IntegrationTestSetup:
    flask_client: FlaskClient
    db_client: DatabaseClient
    tus: TestUserSetup
