from datetime import date
from typing import Generator

import pytest
from starlette.testclient import TestClient

from app import create_fast_api_app
from db.client.core import DatabaseClient
from db.enums import (
    AgencyAggregation,
    DetailLevel,
    AccessType,
    UpdateMethod,
    RetentionSchedule,
    URLStatus,
)
from db.models.implementations import LinkAgencyMetaURL
from db.models.implementations.links.agency__data_source import LinkAgencyDataSource
from db.models.implementations.core.agency.meta_urls.sqlalchemy import MetaURL
from db.models.implementations.core.data_source.core import DataSource
from middleware.enums import (
    PermissionsEnum,
    AccessTypeEnum,
)
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.fastapi import (
    get_source_collector_data_sources_access_info,
    get_standard_access_info, access_with, access_with_read_all_user_info, access_with_user_create_update,
)
from tests.helpers.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)
from tests.integration.v3.helpers.api_test_helper import APITestHelper
from tests.integration.v3.helpers.request_validator import RequestValidatorFastAPI

MOCK_USER_ID = 1


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    app = create_fast_api_app()
    with TestClient(app) as c:
        app.dependency_overrides[get_source_collector_data_sources_access_info] = (
            lambda: AccessInfoPrimary(
                user_id=MOCK_USER_ID,
                permissions=[
                    PermissionsEnum.SOURCE_COLLECTOR_DATA_SOURCES,
                    PermissionsEnum.SOURCE_COLLECTOR,
                    PermissionsEnum.SOURCE_COLLECTOR_FINAL_REVIEW,
                ],
                user_email="test@example.com",
                access_type=AccessTypeEnum.JWT,
            )
        )
        app.dependency_overrides[access_with_read_all_user_info] = lambda: AccessInfoPrimary(
            user_id=MOCK_USER_ID,
            permissions=[
                PermissionsEnum.READ_ALL_USER_INFO,
            ],
            user_email="test@example.com",
            access_type=AccessTypeEnum.JWT,
        )
        app.dependency_overrides[access_with_user_create_update] = lambda: AccessInfoPrimary(
            user_id=MOCK_USER_ID,
            permissions=[
                PermissionsEnum.USER_CREATE_UPDATE,
            ],
            user_email="test@example.com",
            access_type=AccessTypeEnum.JWT,
        )
        app.dependency_overrides[get_standard_access_info] = lambda: AccessInfoPrimary(
            user_id=MOCK_USER_ID,
            permissions=[],
            user_email="test@example.com",
            access_type=AccessTypeEnum.JWT,
        )

        yield c


@pytest.fixture
def api_test_helper(
    client: TestClient, test_data_creator_db_client: TestDataCreatorDBClient
) -> Generator[APITestHelper, None, None]:
    yield APITestHelper(
        request_validator=RequestValidatorFastAPI(client),
        db_data_creator=test_data_creator_db_client,
    )


@pytest.fixture
def data_source_id_1(agency_id_1: int, live_database_client: DatabaseClient) -> int:
    data_source = DataSource(
        name="Test Data Source",
        description="Test Description",
        source_url="https://www.example.com/",
        agency_supplied=True,
        supplying_entity="Test supplying entity",
        agency_aggregation=AgencyAggregation.LOCAL.value,
        coverage_start=date(year=2023, month=7, day=5),
        coverage_end=date(year=2024, month=7, day=5),
        detail_level=DetailLevel.INDIVIDUAL.value,
        access_types=[AccessType.API.value, AccessType.DOWNLOAD.value],
        data_portal_type="Test Data Portal Type",
        record_formats=["Test Record Format"],
        update_method=UpdateMethod.OVERWRITE.value,
        readme_url="https://www.example.com/readme",
        originating_entity="Test originating entity",
        retention_schedule=RetentionSchedule.LESS_THAN_ONE_DAY.value,
        scraper_url="https://www.example.com/scraper",
        agency_described_not_in_database="Test agency described not in database",
        data_portal_type_other="Test other data portal type",
        access_notes="Test access notes",
        url_status=URLStatus.OK.value,
        record_type_id=1,
    )

    data_source_id: int = live_database_client.add(data_source, return_id=True)

    link = LinkAgencyDataSource(
        agency_id=agency_id_1,
        data_source_id=data_source_id,
    )
    live_database_client.add(link)

    return data_source_id


@pytest.fixture
def data_source_id_2(agency_id_2: int, live_database_client: DatabaseClient) -> int:
    data_source = DataSource(
        name="Test Data Source",
        description="Test Description",
        source_url="https://www.example.com/2",
        agency_supplied=False,
        supplying_entity=None,
        agency_aggregation=None,
        coverage_start=None,
        coverage_end=None,
        detail_level=None,
        access_types=None,
        data_portal_type=None,
        record_formats=None,
        update_method=None,
        readme_url=None,
        originating_entity=None,
        retention_schedule=None,
        scraper_url=None,
        agency_described_not_in_database=None,
        data_portal_type_other=None,
        access_notes=None,
        url_status=URLStatus.OK.value,
        record_type_id=2,
    )

    data_source_id: int = live_database_client.add(data_source, return_id=True)

    link = LinkAgencyDataSource(
        agency_id=agency_id_2,
        data_source_id=data_source_id,
    )
    live_database_client.add(link)

    return data_source_id


@pytest.fixture
def meta_url_id_1(agency_id_1: int, live_database_client: DatabaseClient) -> int:
    agency_meta_url = MetaURL(
        url="https://www.example.com/agency_meta_url",
    )
    meta_url_id: int = live_database_client.add(agency_meta_url, return_id=True)
    link = LinkAgencyMetaURL(
        agency_id=agency_id_1,
        meta_url_id=meta_url_id,
    )
    live_database_client.add(link)
    return meta_url_id


@pytest.fixture
def meta_url_id_2(agency_id_2: int, live_database_client: DatabaseClient) -> int:
    agency_meta_url = MetaURL(
        url="https://www.example.com/agency_meta_url_2",
    )
    meta_url_id: int = live_database_client.add(agency_meta_url, return_id=True)
    link = LinkAgencyMetaURL(
        agency_id=agency_id_2,
        meta_url_id=meta_url_id,
    )
    live_database_client.add(link)
    return meta_url_id
