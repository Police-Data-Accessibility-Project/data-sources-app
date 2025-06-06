from unittest.mock import ANY

import pytest

from database_client.enums import RequestUrgency
from middleware.schema_and_dto_logic.primary_resource_dtos.data_requests_dtos import (
    RequestInfoPostDTO,
    DataRequestsPostDTO,
)
from tests.conftest import client_with_mock_db, bypass_authentication_required
from tests.helper_scripts.common_mocks_and_patches import (
    patch_and_return_mock,
)
from tests.helper_scripts.constants import DATA_REQUESTS_BASE_ENDPOINT

PATCH_ROOT = "resources.instantiations.data_requests"

STANDARD_REQUEST_INFO_JSON = {
    "submission_notes": "test_sb",
    "title": "test_title",
    "request_urgency": "urgent",
}


@pytest.mark.parametrize(
    "request_info_post_content, expected_request_info_dto",
    (
        [
            (
                {
                    "submission_notes": "test_sb",
                    "title": "test_title",
                    "request_urgency": "urgent",
                },
                RequestInfoPostDTO(
                    submission_notes="test_sb",
                    title="test_title",
                    request_urgency=RequestUrgency.URGENT,
                ),
            )
        ]
    ),
)
@pytest.mark.parametrize(
    "locations_info_post_content, expected_locations_info_dto",
    ([(None, None), ([], None)]),
)
def test_data_requests_post_dto_population(
    request_info_post_content,
    expected_request_info_dto,
    locations_info_post_content,
    expected_locations_info_dto,
    monkeypatch,
    bypass_authentication_required,
    client_with_mock_db,
):
    mock_create_data_request_wrapper = patch_and_return_mock(
        path=f"{PATCH_ROOT}.create_data_request_wrapper",
        monkeypatch=monkeypatch,
        returns_test_response=True,
    )

    json_to_post = {
        "request_info": request_info_post_content,
    }
    if locations_info_post_content is not None:
        json_to_post["location_infos"] = locations_info_post_content

    response = client_with_mock_db.client.post(
        DATA_REQUESTS_BASE_ENDPOINT, json=json_to_post
    )

    mock_create_data_request_wrapper.assert_called_once_with(
        ANY,
        dto=DataRequestsPostDTO(
            request_info=expected_request_info_dto,
            location_ids=expected_locations_info_dto,
        ),
        access_info=ANY,
    )
