import pytest

from database_client.enums import SortOrder
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetManyBaseDTO
from resources.UserProfile import USER_PROFILE_DATA_REQUEST_ENDPOINT_FULL
from tests.helper_scripts.common_mocks_and_patches import patch_and_return_mock
from tests.helper_scripts.constants import (
    GET_MANY_TEST_QUERY_ARGS,
    GET_MANY_TEST_QUERY_PARAMS,
)
from tests.helper_scripts.helper_functions import add_query_params
from tests.resources.conftest import ResourceTestSetup


@pytest.fixture
def user_profile_data_requests_setup(resource_test_setup: ResourceTestSetup):
    rts = resource_test_setup
    rts.mock.get_owner_data_requests_wrapper = patch_and_return_mock(
        "resources.UserProfile.get_owner_data_requests_wrapper", rts.monkeypatch
    )

    return rts

@pytest.mark.parametrize(GET_MANY_TEST_QUERY_ARGS, GET_MANY_TEST_QUERY_PARAMS)
def test_user_profile_data_requests_get_many_parameters(
        query_dict: dict,
        expected_dto: GetManyBaseDTO,
        user_profile_data_requests_setup: ResourceTestSetup,
):
    ts = user_profile_data_requests_setup
    endpoint = add_query_params(
        USER_PROFILE_DATA_REQUEST_ENDPOINT_FULL,
        query_dict,
    )
    response = ts.client_with_mock_db.client.get(endpoint)
    ts.mock.get_owner_data_requests_wrapper.assert_called_once_with(
        ts.mock.db_client,
        access_info=ts.mock.access_info,
        dto=expected_dto,
    )
