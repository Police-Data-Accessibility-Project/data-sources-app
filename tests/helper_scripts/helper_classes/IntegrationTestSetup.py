from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

import pytest
from flask.testing import FlaskClient

from database_client.database_client import DatabaseClient
from tests.helper_scripts.helper_functions import create_test_user_setup
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.simple_result_validators import check_response_status
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup


@dataclass
class IntegrationTestSetup:
    flask_client: FlaskClient
    db_client: DatabaseClient
    tus: TestUserSetup

    def run_and_validate_request(
        self,
        http_method: str,
        endpoint: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        **request_kwargs,
    ):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method=http_method,
            endpoint=endpoint,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            **request_kwargs,
        )


@pytest.fixture
def integration_test_setup(flask_client_with_db: FlaskClient):
    return IntegrationTestSetup(
        flask_client=flask_client_with_db,
        db_client=DatabaseClient(),
        tus=create_test_user_setup(flask_client_with_db),
    )
