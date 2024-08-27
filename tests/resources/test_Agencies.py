from http import HTTPStatus
from tests.fixtures import client_with_mock_db, bypass_api_key_required, bypass_authentication_required
from tests.helper_scripts.helper_functions import run_and_validate_request


def mock_get_agencies(cursor, page: int):
    # This mock function is a bit of a hack:
    # In reality, count would not be equivalent to the page
    # But it's intended to show that the get method
    # properly reads the page parameter.
    return ({"count": page, "data": None}, HTTPStatus.IM_A_TEAPOT)


def test_get_agencies(client_with_mock_db, monkeypatch, bypass_authentication_required):
    monkeypatch.setattr("resources.Agencies.get_agencies", mock_get_agencies)

    run_and_validate_request(
        flask_client=client_with_mock_db.client,
        http_method="get",
        endpoint="agencies/page/3",
        headers={"Authorization": "Bearer test_token"},
        expected_json_content={"count": 3, "data": None},
        expected_response_status=HTTPStatus.IM_A_TEAPOT,
    )
