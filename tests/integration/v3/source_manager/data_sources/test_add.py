from datetime import date

from db.client.core import DatabaseClient
from db.enums import AgencyAggregation, UpdateMethod, RetentionSchedule, AccessType, URLStatus
from db.models.implementations.links.agency__data_source import LinkAgencyDataSource
from db.models.implementations.core.data_source.core import DataSource
from endpoints.v3.source_manager.sync.data_sources.add.request import (
    AddDataSourcesOuterRequest,
    AddDataSourcesInnerRequest,
)
from endpoints.v3.source_manager.sync.data_sources.shared.content import (
    DataSourceSyncContentModel,
)
from endpoints.v3.source_manager.sync.shared.models.response.add import (
    SourceManagerSyncAddOuterResponse,
)
from middleware.enums import RecordTypesEnum
from tests.integration.v3.helpers.api_test_helper import APITestHelper


def test_source_manager_data_sources_add(
    live_database_client: DatabaseClient,
    api_test_helper: APITestHelper,
    agency_id_1: int,
    agency_id_2: int,
):
    api_test_helper.request_validator.post_v3(
        url="/source-manager/data-sources/add",
        json=AddDataSourcesOuterRequest(
            data_sources=[
                AddDataSourcesInnerRequest(
                    request_id=1,
                    content=DataSourceSyncContentModel(
                        source_url="https://www.example.com/",
                        name="test",
                        record_type=RecordTypesEnum.CRIME_STATISTICS,
                        description="Test description",
                        record_formats=["Test Record Format"],
                        data_portal_type="Test Data Portal Type",
                        supplying_entity="Test supplying entity",
                        coverage_start=date(year=2023, month=7, day=5),
                        coverage_end=date(year=2024, month=7, day=5),
                        agency_supplied=True,
                        agency_originated=False,
                        agency_aggregation=AgencyAggregation.LOCAL,
                        agency_described_not_in_database="Test described not in database",
                        update_method=UpdateMethod.NO_UPDATES,
                        readme_url="https://www.example.com/readme",
                        originating_entity="Test originating entity",
                        retention_schedule=RetentionSchedule.LESS_THAN_ONE_DAY,
                        scraper_url="https://www.example.com/scraper",
                        access_notes="Test Access Notes",
                        access_types=[AccessType.API, AccessType.DOWNLOAD],
                        agency_ids=[agency_id_1, agency_id_2],
                        url_status=URLStatus.OK
                    ),
                ),
                AddDataSourcesInnerRequest(
                    request_id=2,
                    content=DataSourceSyncContentModel(
                        source_url="https://www.example.com/2",
                        name="test2",
                        record_type=RecordTypesEnum.GEOGRAPHIC,
                        description="Test description",
                        record_formats=[],
                        data_portal_type=None,
                        supplying_entity=None,
                        coverage_start=None,
                        coverage_end=None,
                        agency_supplied=True,
                        agency_originated=False,
                        agency_aggregation=None,
                        agency_described_not_in_database=None,
                        update_method=None,
                        readme_url=None,
                        originating_entity=None,
                        retention_schedule=None,
                        scraper_url=None,
                        access_notes=None,
                        access_types=[],
                        agency_ids=[agency_id_1],
                        url_status=URLStatus.OK
                    ),
                ),
            ]
        ).model_dump(mode="json"),
        expected_model=SourceManagerSyncAddOuterResponse,
    )

    data_sources: list[dict] = live_database_client.get_all(DataSource)
    assert len(data_sources) == 2

    data_source_1 = data_sources[0]
    assert data_source_1["name"] == "test"
    assert data_source_1["record_type_id"] == 27  # Geographic
    assert data_source_1["description"] == "Test description"
    assert data_source_1["record_formats"] == ["Test Record Format"]
    assert data_source_1["data_portal_type"] == "Test Data Portal Type"
    assert data_source_1["supplying_entity"] == "Test supplying entity"
    assert data_source_1["coverage_start"] == date(year=2023, month=7, day=5)
    assert data_source_1["coverage_end"] == date(year=2024, month=7, day=5)
    assert data_source_1["agency_supplied"] is True
    assert data_source_1["agency_originated"] is False
    assert data_source_1["agency_aggregation"] == AgencyAggregation.LOCAL.value
    assert (
        data_source_1["agency_described_not_in_database"]
        == "Test described not in database"
    )
    assert data_source_1["update_method"] == UpdateMethod.NO_UPDATES.value
    assert data_source_1["readme_url"] == "https://www.example.com/readme"
    assert data_source_1["originating_entity"] == "Test originating entity"
    assert (
        data_source_1["retention_schedule"] == RetentionSchedule.LESS_THAN_ONE_DAY.value
    )
    assert data_source_1["scraper_url"] == "https://www.example.com/scraper"
    assert data_source_1["access_notes"] == "Test Access Notes"
    assert data_source_1["access_types"] == [
        AccessType.API.value,
        AccessType.DOWNLOAD.value,
    ]

    data_source_2 = data_sources[1]
    assert data_source_2["name"] == "test2"
    assert data_source_2["record_type_id"] == 23  # Crime statistics
    assert data_source_2["description"] == "Test description"
    assert data_source_2["record_formats"] == []
    assert data_source_2["data_portal_type"] is None
    assert data_source_2["supplying_entity"] is None
    assert data_source_2["coverage_start"] is None
    assert data_source_2["coverage_end"] is None
    assert data_source_2["agency_supplied"] is True
    assert data_source_2["agency_originated"] is False
    assert data_source_2["agency_aggregation"] is None
    assert data_source_2["agency_described_not_in_database"] is None
    assert data_source_2["update_method"] is None
    assert data_source_2["readme_url"] is None
    assert data_source_2["originating_entity"] is None
    assert data_source_2["retention_schedule"] is None
    assert data_source_2["scraper_url"] is None
    assert data_source_2["access_notes"] is None
    assert data_source_2["access_types"] == []

    # Check links.
    links: list[dict] = live_database_client.get_all(LinkAgencyDataSource)
    assert len(links) == 3
    link_tuples_set = {(link["agency_id"], link["data_source_id"]) for link in links}
    assert link_tuples_set == {
        (agency_id_1, data_source_1["id"]),
        (agency_id_2, data_source_1["id"]),
        (agency_id_1, data_source_2["id"]),
    }
