from middleware.schema_and_dto_logic.primary_resource_dtos.source_collector_dtos import SourceCollectorPostRequestDTO, \
    SourceCollectorPostRequestInnerDTO
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import TestDataCreatorFlask


def test_source_collector(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    agency_ids = [tdc.agency().id for _ in range(3)]

    tus_admin = tdc.get_admin_tus()
    tus_standard = tdc.standard_user()

    # Create one data source which will also be included in the request as a duplicate
    data_source = tdc.data_source()

    dto = SourceCollectorPostRequestDTO(
        data_sources=[
            SourceCollectorPostRequestInnerDTO(
                name="Test Data Source",
                description="Test Data Source Description",
                source_url="http://test.com",
                record_type=RecordTypes.GENERAL,
        ]
    )
