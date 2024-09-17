import pytest
from flask.testing import FlaskClient

from database_client.enums import SortOrder
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetManyBaseDTO
from tests.fixtures import (
    mock_database_client,
    client_with_mock_db,
    ClientWithMockDB,
    bypass_authentication_required,
)
from tests.helper_scripts.common_mocks_and_patches import patch_and_return_mock
from tests.helper_scripts.constants import (
    GET_MANY_TEST_QUERY_PARAMS,
    AGENCIES_BASE_ENDPOINT,
)
from tests.helper_scripts.helper_functions import add_query_params


@pytest.mark.parametrize(
    "query_params, expected_dto",
    GET_MANY_TEST_QUERY_PARAMS,
)
def test_agencies_query_params(
    query_params: dict,
    expected_dto: GetManyBaseDTO,
    mock_database_client,
    client_with_mock_db: ClientWithMockDB,
    bypass_authentication_required,
    monkeypatch,
):
    mock_access_info = bypass_authentication_required
    mock_get_agencies = patch_and_return_mock(
        "resources.Agencies.get_agencies", monkeypatch
    )
    client_with_mock_db.client.get(
        add_query_params(AGENCIES_BASE_ENDPOINT, query_params)
    )
    mock_get_agencies.assert_called_once_with(
        mock_database_client, access_info=mock_access_info, dto=expected_dto
    )
