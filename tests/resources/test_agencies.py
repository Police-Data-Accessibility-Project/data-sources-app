from http import HTTPStatus

import pytest
from flask.testing import FlaskClient
from marshmallow import fields

from database_client.enums import SortOrder, LocationType
from middleware.enums import JurisdictionType, AgencyType
from middleware.primary_resource_logic.agencies import (
    AgenciesPostDTO,
    AgencyInfoPostDTO,
    LocationInfoDTO,
    AgenciesPutDTO,
    AgencyInfoPutDTO,
    AgencyInfoPutSchema,
)
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
from tests.helper_scripts.simple_result_validators import check_response_status


@pytest.mark.parametrize(
    "query_params, expected_dto",
    GET_MANY_TEST_QUERY_PARAMS,
)
def test_agencies_get_many_query_params(
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
    response = client_with_mock_db.client.get(
        add_query_params(AGENCIES_BASE_ENDPOINT, query_params)
    )
    mock_get_agencies.assert_called_once_with(
        mock_database_client, access_info=mock_access_info, dto=expected_dto
    )


def test_agencies_post_json_full(
    client_with_mock_db: ClientWithMockDB,
    mock_database_client,
    bypass_authentication_required,
    monkeypatch,
):
    """
    Test that the full suite of expected DTOs are when all possible json fields are included
    :param client_with_mock_db:
    :param mock_database_client:
    :param bypass_authentication_required:
    :param monkeypatch:
    :return:
    """
    mock_access_info = bypass_authentication_required
    mock_create_agency = patch_and_return_mock(
        "resources.Agencies.create_agency", monkeypatch
    )

    json_to_include = {
        "agency_info": {
            "submitted_name": "test_agency_name",
            "homepage_url": "test_homepage_url",
            "jurisdiction_type": JurisdictionType.STATE.value,
            "lat": 1.3,
            "lng": 4.8,
            "defunct_year": "test_defunct_year",
            "airtable_uid": "test_airtable_uid",
            "agency_type": AgencyType.JAIL.value,
            "multi_agency": True,
            "zip_code": "12345",
            "no_web_presence": True,
            "approved": True,
            "rejection_reason": "test_rejection_reason",
            "last_approval_editor": "test_last_approval_editor",
            "submitter_contact": "test_submitter_contact",
        },
        "location_info": {
            "type": LocationType.LOCALITY.value,
            "state_iso": "CA",
            "county_fips": "54321",
            "locality_name": "San Francisco",
        },
    }

    response = client_with_mock_db.client.post(
        AGENCIES_BASE_ENDPOINT, json=json_to_include
    )

    mock_create_agency.assert_called_once_with(
        mock_database_client,
        access_info=mock_access_info,
        dto=AgenciesPostDTO(
            agency_info=AgencyInfoPostDTO(
                submitted_name="test_agency_name",
                homepage_url="test_homepage_url",
                jurisdiction_type=JurisdictionType.STATE,
                lat=1.3,
                lng=4.8,
                defunct_year="test_defunct_year",
                airtable_uid="test_airtable_uid",
                agency_type=AgencyType.JAIL,
                multi_agency=True,
                zip_code="12345",
                no_web_presence=True,
                approved=True,
                rejection_reason="test_rejection_reason",
                last_approval_editor="test_last_approval_editor",
                submitter_contact="test_submitter_contact",
            ),
            location_info=LocationInfoDTO(
                type=LocationType.LOCALITY,
                state_iso="CA",
                county_fips="54321",
                locality_name="San Francisco",
            ),
        ),
    )


def test_agencies_post_json_minimal_no_location_info(
    client_with_mock_db: ClientWithMockDB,
    mock_database_client,
    bypass_authentication_required,
    monkeypatch,
):
    """
    Test that the expected DTOs are produced when the minimum number of JSON fields are produced,
    including no location info
    :param client_with_mock_db:
    :param mock_database_client:
    :param bypass_authentication_required:
    :param monkeypatch:
    :return:
    """
    mock_access_info = bypass_authentication_required
    mock_create_agency = patch_and_return_mock(
        "resources.Agencies.create_agency", monkeypatch
    )

    json_to_include = {
        "agency_info": {
            "submitted_name": "test_agency_name",
            "jurisdiction_type": JurisdictionType.FEDERAL.value,
            "airtable_uid": "test_airtable_uid",
            "agency_type": AgencyType.JAIL.value,
        }
    }

    response = client_with_mock_db.client.post(
        AGENCIES_BASE_ENDPOINT, json=json_to_include
    )

    mock_create_agency.assert_called_once_with(
        mock_database_client,
        access_info=mock_access_info,
        dto=AgenciesPostDTO(
            agency_info=AgencyInfoPostDTO(
                submitted_name="test_agency_name",
                homepage_url=None,
                jurisdiction_type=JurisdictionType.FEDERAL,
                lat=None,
                lng=None,
                defunct_year=None,
                airtable_uid="test_airtable_uid",
                agency_type=AgencyType.JAIL,
                multi_agency=False,
                zip_code=None,
                no_web_presence=False,
                approved=False,
                rejection_reason=None,
                last_approval_editor=None,
                submitter_contact=None,
            ),
            location_info=None,
        ),
    )


def test_agencies_post_json_minimal_with_location_info(
    client_with_mock_db: ClientWithMockDB,
    mock_database_client,
    bypass_authentication_required,
    monkeypatch,
):
    """
    Test that the expected DTOs are produced when the minimum number of JSON fields are produced,
    with a minimum of location info parameters included
    :param client_with_mock_db:
    :param mock_database_client:
    :param bypass_authentication_required:
    :param monkeypatch:
    :return:
    """
    mock_access_info = bypass_authentication_required
    mock_create_agency = patch_and_return_mock(
        "resources.Agencies.create_agency", monkeypatch
    )

    json_to_include = {
        "agency_info": {
            "submitted_name": "test_agency_name",
            "jurisdiction_type": JurisdictionType.STATE.value,
            "airtable_uid": "test_airtable_uid",
            "agency_type": AgencyType.JAIL.value,
        },
        "location_info": {
            "type": LocationType.STATE.value,
            "state_iso": "CA",
        },
    }

    response = client_with_mock_db.client.post(
        AGENCIES_BASE_ENDPOINT, json=json_to_include
    )

    mock_create_agency.assert_called_once_with(
        mock_database_client,
        access_info=mock_access_info,
        dto=AgenciesPostDTO(
            agency_info=AgencyInfoPostDTO(
                submitted_name="test_agency_name",
                homepage_url=None,
                jurisdiction_type=JurisdictionType.STATE,
                lat=None,
                lng=None,
                defunct_year=None,
                airtable_uid="test_airtable_uid",
                agency_type=AgencyType.JAIL,
                multi_agency=False,
                zip_code=None,
                no_web_presence=False,
                approved=False,
                rejection_reason=None,
                last_approval_editor=None,
                submitter_contact=None,
            ),
            location_info=LocationInfoDTO(
                type=LocationType.STATE,
                state_iso="CA",
                county_fips=None,
                locality_name=None,
            ),
        ),
    )

