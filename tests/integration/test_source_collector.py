from middleware.enums import RecordTypes
from middleware.schema_and_dto_logic.primary_resource_dtos.source_collector_dtos import SourceCollectorPostRequestDTO, \
    SourceCollectorPostRequestInnerDTO
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import TestDataCreatorFlask


def test_source_collector(
        test_data_creator_flask: TestDataCreatorFlask
):
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
                record_type=RecordTypes.PERSONNEL_RECORDS,
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
                last_approval_editor=tus_standard.user_info.user_id,
                agency_ids=agency_ids[:2],
            )
        ]
    )

    response = tdc.request_validator.source_collector_data_sources(
        headers=tus_admin.jwt_authorization_header,
        dto=dto
    )

    assert len(response["data_sources"]) == 3
    response_1 = response["data_sources"][0]
    assert response_1["data_source_id"] is not None, response_1['error']
    data_source_id_1 = response_1["data_source_id"]
    assert response_1['error'] is None
    assert response_1['status'] == 'success'
    assert response_1['url'] == dto.data_sources[0].source_url

    response_2 = response["data_sources"][1]
    assert response_2["data_source_id"] is None
    assert response_2['error'] is not None
    assert response_2['status'] == 'failure'
    assert response_2['url'] is None

    response_3 = response["data_sources"][2]
    assert response_3["data_source_id"] is not None
    data_source_id_3 = response_3["data_source_id"]
    assert response_3['error'] is None
    assert response_3['status'] == 'success'
    assert response_3['url'] == dto.data_sources[2].source_url

    pass

    # TODO: Add tests that middle one errs, and other two are added to database with requisite info
