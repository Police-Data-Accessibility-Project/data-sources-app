from http import HTTPStatus

from tests.conftest import dev_db_client, flask_client_with_db
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.common_asserts import assert_response_status


def test_api_doc_load(flask_client_with_db):
    """
    Call the API doc endpoint and confirm it returns a 200 status
    :param flask_client_with_db:
    :return:
    """

    response = flask_client_with_db.open(
        "/api/swagger.json", method="get", follow_redirects=True
    )
    assert_response_status(response, HTTPStatus.OK)
    print(response)
