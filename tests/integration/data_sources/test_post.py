from datetime import date

from db.enums import AgencyAggregation, UpdateMethod, RetentionSchedule, AccessType
from endpoints.instantiations.data_sources_.post.request_.endpoint_schema_config import (
    PostDataSourceRequestEndpointSchemaConfig,
)
from endpoints.instantiations.data_sources_.post.request_.model import (
    PostDataSourceOuterRequest,
    PostDataSourceRequest,
)
from middleware.enums import RecordTypesEnum
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask


def test_post_data_source(
    test_data_creator_flask: TestDataCreatorFlask, agency_id_1: int, agency_id_2: int
):
    test_data_creator_flask.request_validator.post(
        endpoint="/data-sources",
        headers=test_data_creator_flask.standard_user().jwt_authorization_header,
        json=PostDataSourceOuterRequest(
            entry_data=PostDataSourceRequest(
                source_url="https://www.example.com/",
                name="test",
                record_type_name=RecordTypesEnum.CRIME_STATISTICS,
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
            ),
            linked_agency_ids=[agency_id_1, agency_id_2],
        ).model_dump(mode="json"),
        expected_schema=PostDataSourceRequestEndpointSchemaConfig.primary_output_schema,
    )
