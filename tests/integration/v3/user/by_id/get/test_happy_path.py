from datetime import date

from db.client.core import DatabaseClient
from db.client.helpers import run_query_builder
from db.enums import RequestStatus, RequestUrgency, URLStatus, AgencyAggregation, DetailLevel, AccessType, UpdateMethod, \
    RetentionSchedule, ExternalAccountTypeEnum
from db.helpers_.record_type.mapper import RecordTypeMapper
from db.helpers_.record_type.query import GetRecordTypeMapperQueryBuilder
from db.models.implementations import LinkRecentSearchRecordTypes, LinkRecentSearchRecordCategories, \
    LinkLocationDataRequest, LinkAgencyDataSource, LinkDataSourceDataRequest
from db.models.implementations.core.data_request.core import DataRequest
from db.models.implementations.core.data_request.github_issue_info import DataRequestsGithubIssueInfo
from db.models.implementations.core.data_source.core import DataSource
from db.models.implementations.core.external_account import ExternalAccount
from db.models.implementations.core.recent_search.core import RecentSearch
from db.models.implementations.core.user.permission import UserPermission
from db.models.implementations.links.user__followed_location import LinkUserFollowedLocation
from middleware.enums import RecordTypesEnum
from tests.helpers.helper_classes.test_data_creator.db_client_.core import TestDataCreatorDBClient
from tests.helpers.test_dataclasses import TestUserDBInfo
from tests.integration.v3.helpers.api_test_helper import APITestHelper
from tests.integration.v3.helpers.request_validator import RequestValidatorFastAPI
from utilities.enums import RecordCategoryEnum


def test_happy_path(
    test_data_creator_db_client: TestDataCreatorDBClient,
    api_test_helper: APITestHelper,
    pittsburgh_id: int,
    national_id: int,
    agency_id_1: int,
    agency_id_2: int
):
    rv: RequestValidatorFastAPI = api_test_helper.request_validator
    tdc = test_data_creator_db_client
    db_client: DatabaseClient = tdc.db_client
    record_type_mapper: RecordTypeMapper = run_query_builder(GetRecordTypeMapperQueryBuilder())

    # Create User
    tus: TestUserDBInfo = tdc.user()

    # Create Recent Search with location, no record types or record categories
    rs_pittsburgh = RecentSearch(
        user_id=tus.id,
        location_id=pittsburgh_id,
    )
    rs_pittsburgh_id: int = db_client.add(rs_pittsburgh, return_id=True)

    # Create Recent Search with national location, record type link
    rs_national = RecentSearch(
        user_id=tus.id,
        location_id=national_id,
    )
    rs_national_id: int = db_client.add(rs_national, return_id=True)
    ## Record Type Link (2)
    rs_national_link_1 = LinkRecentSearchRecordTypes(
        recent_search_id=rs_national_id,
        record_type_id=record_type_mapper.get_record_type_id_by_record_type(
            RecordTypesEnum.ACCIDENT_REPORTS
        ),
    )
    rs_national_link_2 = LinkRecentSearchRecordTypes(
        recent_search_id=rs_national_id,
        record_type_id=record_type_mapper.get_record_type_id_by_record_type(
            RecordTypesEnum.BOOKING_REPORTS
        ),
    )
    db_client.add_many([
        rs_national_link_1,
        rs_national_link_2,
    ])


    # Create Recent Search with no location, record category links
    rs_no_loc = RecentSearch(
        user_id=tus.id,
    )
    rs_no_loc_id: int = db_client.add(rs_no_loc, return_id=True)
    ## Record Category Link (1)
    rs_no_loc_link_1 = LinkRecentSearchRecordCategories(
        recent_search_id=rs_no_loc_id,
        record_category_id=record_type_mapper.get_record_category_id_by_record_category(
            RecordCategoryEnum.JAIL
        ),
    )
    db_client.add(rs_no_loc_link_1)

    # Have the user follow a locality search
    link_user_followed_location = LinkUserFollowedLocation(
        user_id=tus.id,
        location_id=pittsburgh_id,
    )
    db_client.add(link_user_followed_location)

    # Have the user create a minimal data request
    data_request_minimal = DataRequest(
        request_status=RequestStatus.INTAKE.value,
        creator_user_id=tus.id,
        title="Data Request Minimal Test"
    )
    data_request_minimal_id: int = db_client.add(
        data_request_minimal,
        return_id=True
    )

    # TODO: Have the user created a data request with all attributes filled
    data_request_all_attributes = DataRequest(
        submission_notes="Test submission notes",
        request_status=RequestStatus.ARCHIVED.value,
        archive_reason="Test Archive Reason",
        creator_user_id=tus.id,
        internal_notes="Test Internal Notes",
        record_types_required=[
            RecordTypesEnum.RECORDS_REQUEST_INFO.value,
            RecordTypesEnum.CRIME_STATISTICS.value
        ],
        pdap_response="Test PDAP Response",
        coverage_range="Test Coverage Range",
        data_requirements="Test Data Requirements",
        request_urgency=RequestUrgency.LONG_TERM.value,
        title="Data Request All Attributes Test"
    )
    data_request_all_attributes_id: int = db_client.add(
        data_request_all_attributes,
        return_id=True
    )
    ## Add location to data request
    link_location_data_request = LinkLocationDataRequest(
        location_id=pittsburgh_id,
        data_request_id=data_request_all_attributes_id
    )
    db_client.add(link_location_data_request)

    ## Add Github Issue Info
    github_issue_info = DataRequestsGithubIssueInfo(
        github_issue_url="https://github.com/test-repo/issue/21",
        github_issue_number=21,
        data_request_id=data_request_all_attributes_id
    )
    db_client.add(github_issue_info)

    ## Add Data Sources, and Link To Data Request
    ### Add Minimal Data Source
    data_source_minimal = DataSource(
        name="Test Data Source Minimal",
        url_status=URLStatus.OK.value,
        record_type_id=record_type_mapper.get_record_type_id_by_record_type(
            RecordTypesEnum.MEDIA_BULLETINS
        ),
    )
    data_source_minimal_id: int = db_client.add(
        data_source_minimal,
        return_id=True
    )
    #### Link To Agency
    link_data_source_minimal_to_agency = LinkAgencyDataSource(
        data_source_id=data_source_minimal_id,
        agency_id=agency_id_1
    )
    db_client.add(link_data_source_minimal_to_agency)
    #### Link to Data Request
    link_data_source_minimal_to_data_request = LinkDataSourceDataRequest(
        data_source_id=data_source_minimal_id,
        request_id=data_request_minimal_id
    )
    db_client.add(link_data_source_minimal_to_data_request)

    ### Add Data Source with all attributes filled
    data_source_all_attributes = DataSource(
        name="Test Data Source All Attributes",
        description="Test Data Source All Attributes Description",
        url_status=URLStatus.BROKEN.value,
        source_url="https://test.com",
        agency_supplied=True,
        supplying_entity="Test Supplying Entity",
        agency_originated=False,
        agency_aggregation=AgencyAggregation.LOCAL,
        coverage_start=date(year=2020, month=8, day=3),
        coverage_end=date(year=2020, month=8, day=4),
        detail_level=DetailLevel.AGGREGATED,
        access_types=[
            AccessType.DOWNLOAD,
            AccessType.API
        ],
        data_portal_type="CKAN",
        record_formats=[
            "Test Record Format 1",
            "Test Record Format 2",
        ],
        readme_url="https://test.com/readme",
        originating_entity="Test Originating Entity",
        retention_schedule=RetentionSchedule.FUTURE_ONLY,
        scraper_url="https://test.com/scraper",
        agency_described_not_in_database="Test Agency Described Not In Database",
        data_portal_type_other="Test Data Portal Type",
        access_notes="Test Access Notes",
        update_method=UpdateMethod.OVERWRITE,
        record_type_id=record_type_mapper.get_record_type_id_by_record_type(
            RecordTypesEnum.CAR_GPS
        ),
    )
    data_source_all_attributes_id: int = db_client.add(
        data_source_all_attributes,
        return_id=True
    )
    #### Link To Agency
    link_data_source_all_attributes_to_agency = LinkAgencyDataSource(
        data_source_id=data_source_all_attributes_id,
        agency_id=agency_id_1
    )
    db_client.add(link_data_source_all_attributes_to_agency)
    #### Link to Data Request
    link_data_source_all_attributes_to_data_request = LinkDataSourceDataRequest(
        data_source_id=data_source_all_attributes_id,
        request_id=data_request_all_attributes_id
    )
    db_client.add(link_data_source_all_attributes_to_data_request)

    # Assign the user a permission
    user_permission = UserPermission(
        user_id=tus.id,
        permission_id=1
    )
    db_client.add(user_permission)

    # Link the user to a fictional github account
    external_account = ExternalAccount(
        account_type=ExternalAccountTypeEnum.GITHUB.value,
        account_identifier=123,
        user_id=tus.id
    )
    db_client.add(external_account)

    # TODO: Call user profile endpoint and confirm it returns results



    # TODO: Test that admin can also get this user's information

    # TODO: Test that other non-admin users cannot get this user's information
