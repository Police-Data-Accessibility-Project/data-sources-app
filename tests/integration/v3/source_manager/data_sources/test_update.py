from datetime import date

from db.client.core import DatabaseClient
from db.enums import (
    DetailLevel,
    AccessType,
    UpdateMethod,
    RetentionSchedule,
    URLStatus,
    AgencyAggregation,
)
from db.models.implementations.links.agency__data_source import LinkAgencyDataSource
from db.models.implementations.core.data_source.core import DataSource
from endpoints.v3.source_manager.sync.data_sources.shared.content import (
    DataSourceSyncContentModel,
)
from endpoints.v3.source_manager.sync.data_sources.update.request import (
    UpdateDataSourcesOuterRequest,
    UpdateDataSourcesInnerRequest,
)
from middleware.enums import RecordTypesEnum
from tests.integration.v3.helpers.api_test_helper import APITestHelper


def test_data_source_manager_data_sources_update(
    live_database_client: DatabaseClient,
    api_test_helper: APITestHelper,
    data_source_id_1: int,
    data_source_id_2: int,
    agency_id_1: int,
    agency_id_2: int,
):
    api_test_helper.request_validator.post_v3(
        url="/sync/data-sources/update",
        json=UpdateDataSourcesOuterRequest(
            data_sources=[
                # The majority of these are left undefined to test that they are not updated
                UpdateDataSourcesInnerRequest(
                    app_id=data_source_id_1,
                    content=DataSourceSyncContentModel(
                        source_url="https://updated-data-source.com/",
                        name="Updated Data Source",
                        record_type=RecordTypesEnum.CAR_GPS,
                        agency_ids=[agency_id_1],
                        url_status=URLStatus.OK,
                    ),
                ),
                UpdateDataSourcesInnerRequest(
                    app_id=data_source_id_2,
                    content=DataSourceSyncContentModel(
                        source_url="https://updated-data-source-2.com/",
                        name="Updated Data Source 2",
                        record_type=RecordTypesEnum.RECORDS_REQUEST_INFO,
                        description="Updated Data Source Description",
                        record_formats=["Updated Record Format"],
                        data_portal_type="Updated Data Portal Type",
                        supplying_entity="Updated supplying entity",
                        coverage_start=date(year=2023, month=7, day=5),
                        coverage_end=date(year=2024, month=7, day=5),
                        detail_level=DetailLevel.INDIVIDUAL,
                        access_types=[AccessType.API, AccessType.DOWNLOAD],
                        update_method=UpdateMethod.OVERWRITE,
                        readme_url="https://www.example.com/readme",
                        originating_entity="Updated originating entity",
                        retention_schedule=RetentionSchedule.LESS_THAN_ONE_DAY,
                        scraper_url="https://www.example.com/scraper",
                        agency_described_not_in_database="Updated agency described not in database",
                        data_portal_type_other="Updated other data portal type",
                        access_notes="Updated access notes",
                        url_status=URLStatus.OK,
                        internet_archive_url="https://www.example.com/internet-archive",
                        agency_supplied=None,
                        agency_ids=[agency_id_1, agency_id_2],
                    ),
                ),
            ]
        ).model_dump(mode="json", exclude_unset=True),
    )

    data_sources: list[dict] = live_database_client.get_all(DataSource)
    assert len(data_sources) == 2
    id_to_data_source = {data_source["id"]: data_source for data_source in data_sources}

    data_source_1 = id_to_data_source[data_source_id_1]
    assert data_source_1["source_url"] == "https://updated-data-source.com/"
    assert data_source_1["name"] == "Updated Data Source"
    assert data_source_1["description"] == "Test Description"
    assert data_source_1["agency_supplied"] is True
    assert data_source_1["supplying_entity"] == "Test supplying entity"
    assert data_source_1["agency_aggregation"] == AgencyAggregation.LOCAL.value
    assert data_source_1["coverage_start"] == date(year=2023, month=7, day=5)
    assert data_source_1["coverage_end"] == date(year=2024, month=7, day=5)
    assert data_source_1["detail_level"] == DetailLevel.INDIVIDUAL.value
    assert data_source_1["data_portal_type"] == "Test Data Portal Type"
    assert data_source_1["record_formats"] == ["Test Record Format"]
    assert data_source_1["update_method"] == UpdateMethod.OVERWRITE.value
    assert data_source_1["readme_url"] == "https://www.example.com/readme"
    assert data_source_1["originating_entity"] == "Test originating entity"
    assert (
        data_source_1["retention_schedule"] == RetentionSchedule.LESS_THAN_ONE_DAY.value
    )
    assert data_source_1["scraper_url"] == "https://www.example.com/scraper"
    assert (
        data_source_1["agency_described_not_in_database"]
        == "Test agency described not in database"
    )
    assert data_source_1["data_portal_type_other"] == "Test other data portal type"
    assert data_source_1["access_notes"] == "Test access notes"
    assert data_source_1["url_status"] == URLStatus.OK.value
    assert data_source_1["record_type_id"] == 1

    data_source_2 = id_to_data_source[data_source_id_2]
    # Should be unchanged
    assert data_source_2["name"] == "Updated Data Source 2"
    assert data_source_2["record_type_id"] == 2
    assert data_source_2["agency_aggregation"] is None

    # Should be modified
    assert data_source_2["source_url"] == "https://updated-data-source-2.com/"
    assert data_source_2["description"] == "Updated Data Source Description"
    assert data_source_2["record_formats"] == ["Updated Record Format"]
    assert data_source_2["data_portal_type"] == "Updated Data Portal Type"
    assert data_source_2["supplying_entity"] == "Updated supplying entity"
    assert data_source_2["coverage_start"] == date(year=2023, month=7, day=5)
    assert data_source_2["coverage_end"] == date(year=2024, month=7, day=5)
    assert data_source_2["detail_level"] == DetailLevel.INDIVIDUAL.value
    assert data_source_2["access_types"] == [
        AccessType.API.value,
        AccessType.DOWNLOAD.value,
    ]
    assert data_source_2["update_method"] == UpdateMethod.OVERWRITE.value
    assert data_source_2["readme_url"] == "https://www.example.com/readme"
    assert data_source_2["originating_entity"] == "Updated originating entity"
    assert (
        data_source_2["retention_schedule"] == RetentionSchedule.LESS_THAN_ONE_DAY.value
    )
    assert data_source_2["scraper_url"] == "https://www.example.com/scraper"
    assert (
        data_source_2["agency_described_not_in_database"]
        == "Updated agency described not in database"
    )
    assert data_source_2["data_portal_type_other"] == "Updated other data portal type"
    assert data_source_2["access_notes"] == "Updated access notes"
    assert data_source_2["url_status"] == URLStatus.OK.value
    assert data_source_2["agency_supplied"] is None
    assert (
        data_source_2["internet_archive_url"]
        == "https://www.example.com/internet-archive"
    )

    # Test Links
    links: list[dict] = live_database_client.get_all(LinkAgencyDataSource)
    assert len(links) == 3
    link_tuples: set[tuple[int, int]] = {
        (link["agency_id"], link["data_source_id"]) for link in links
    }
    assert link_tuples == {
        (agency_id_1, data_source_id_1),
        (agency_id_2, data_source_id_2),
        (agency_id_1, data_source_id_2),
    }
