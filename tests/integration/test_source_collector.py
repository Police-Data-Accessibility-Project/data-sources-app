from http import HTTPStatus

from middleware.enums import RecordTypes, PermissionsEnum
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)
from endpoints.instantiations.source_collector.data_sources.post.dtos.request import (
    SourceCollectorPostRequestInnerDTO,
    SourceCollectorPostRequestDTO,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)


def test_source_collector(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    tdc.clear_test_data()

    agency_ids = [int(tdc.agency().id) for _ in range(3)]

    tus_admin = tdc.get_admin_tus()
    tus_standard = tdc.standard_user()
    tus_source_collector = tdc.user_with_permissions(
        permissions=[PermissionsEnum.SOURCE_COLLECTOR_DATA_SOURCES]
    )

    # Create one data source which will also be included in the request as a duplicate
    data_source = tdc.data_source()

    dto = SourceCollectorPostRequestDTO(
        data_sources=[
            SourceCollectorPostRequestInnerDTO(
                name="Test Data Source",
                description="Test Data Source Description",
                source_url="http://test.com",
                record_type=RecordTypes.INCARCERATION_RECORDS,
                record_formats=["CSV"],
                data_portal_type="test",
                last_approval_editor=tus_standard.user_info.user_id,
                supplying_entity="Test Supplying Entity",
                agency_ids=agency_ids,
            ),
            SourceCollectorPostRequestInnerDTO(
                name=data_source.name,
                description="Test Data Source Description",
                source_url=data_source.url,
                record_type=RecordTypes.ARREST_RECORDS.value,  # This should trigger a duplicate error
                record_formats=["CSV"],
                data_portal_type="test",
                last_approval_editor=tus_admin.user_info.user_id,
                supplying_entity="Test Supplying Entity",
                agency_ids=agency_ids[1:],
            ),
            SourceCollectorPostRequestInnerDTO(
                name="Test Data Source 2",
                description="Test Data Source Description",
                source_url="http://new_test.com",
                record_type=RecordTypes.PERSONNEL_RECORDS,
                last_approval_editor=tus_admin.user_info.user_id,
                agency_ids=agency_ids[:2],
            ),
        ]
    )

    # Try initially with standard user and be denied
    response = tdc.request_validator.source_collector_data_sources(
        headers=tus_standard.jwt_authorization_header,
        dto=dto,
        expected_response_status=HTTPStatus.FORBIDDEN,
        expected_schema=MessageSchema(),
    )

    # Try with source collector and succeed
    response = tdc.request_validator.source_collector_data_sources(
        headers=tus_source_collector.jwt_authorization_header, dto=dto
    )

    assert len(response["data_sources"]) == 3
    response_1 = response["data_sources"][0]
    assert response_1["data_source_id"] is not None, response_1["error"]
    data_source_id_1 = response_1["data_source_id"]
    assert response_1["error"] is None
    assert response_1["status"] == "success"
    assert response_1["url"] == dto.data_sources[0].source_url

    response_2 = response["data_sources"][1]
    assert response_2["data_source_id"] is None
    assert response_2["error"] is not None
    assert response_2["status"] == "failure"
    assert response_2["url"] is not None

    response_3 = response["data_sources"][2]
    assert response_3["data_source_id"] is not None
    data_source_id_3 = response_3["data_source_id"]
    assert response_3["error"] is None
    assert response_3["status"] == "success"
    assert response_3["url"] == dto.data_sources[2].source_url

    data_sources = tdc.request_validator.get_data_sources(
        headers=tus_admin.jwt_authorization_header
    )["data"]

    assert len(data_sources) == 3
    assert data_sources[0]["id"] == int(data_source.id)
    assert data_sources[1]["id"] == int(data_source_id_1)
    assert data_sources[2]["id"] == int(data_source_id_3)

    for data_source in data_sources:
        assert data_source["approval_status"] == "approved"

    # Check submission notes
    assert data_sources[1]["submission_notes"] == "Auto-submitted from Source Collector"
    assert data_sources[2]["submission_notes"] == "Auto-submitted from Source Collector"

    # Check last approval editor
    assert data_sources[1]["last_approval_editor"] == tus_standard.user_info.user_id
    assert data_sources[2]["last_approval_editor"] == tus_admin.user_info.user_id

    # Check supplying entity
    assert data_sources[1]["supplying_entity"] == "Test Supplying Entity"
    assert data_sources[2]["supplying_entity"] is None

    # Check data portal type
    assert data_sources[1]["data_portal_type"] == "test"
    assert data_sources[2]["data_portal_type"] is None

    # Check record type
    assert data_sources[1]["record_type_id"] == 35  # Incarceration Records
    assert data_sources[2]["record_type_id"] == 19  # Personnel Records

    # Check record formats
    assert data_sources[1]["record_formats"] == ["CSV"]
    assert data_sources[2]["record_formats"] is None

    # Check source url
    assert data_sources[1]["source_url"] == "http://test.com"
    assert data_sources[2]["source_url"] == "http://new_test.com"

    # Check agencies
    ds_1_agency_ids = sorted([agency["id"] for agency in data_sources[1]["agencies"]])
    assert ds_1_agency_ids == agency_ids

    ds_2_agency_ids = [agency["id"] for agency in data_sources[2]["agencies"]]
    assert ds_2_agency_ids == agency_ids[:2]


def test_source_collector_duplicates(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    extant_data_sources = []
    for i in range(50):
        data_source = tdc.data_source()
        extant_data_sources.append(data_source)

    tdc.db_client.refresh_materialized_view("DISTINCT_SOURCE_URLS")

    extant_urls = [data_source.url for data_source in extant_data_sources]
    new_urls = ["https://test.com" + str(i) for i in range(50, 100)]

    data = tdc.request_validator.post_source_collector_duplicates(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        urls=extant_urls + new_urls,
    )
    assert len(data["results"]) == 100
    for url in new_urls:
        assert data["results"][url] == False
    for url in extant_urls:
        assert data["results"][url] == True
