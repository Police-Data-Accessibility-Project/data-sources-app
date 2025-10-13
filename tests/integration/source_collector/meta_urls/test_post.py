from db.models.implementations.core.agency.meta_urls.sqlalchemy import AgencyMetaURL
from endpoints.instantiations.source_collector.meta_urls.post.dtos.request import (
    SourceCollectorMetaURLPostRequestInnerDTO,
    SourceCollectorMetaURLPostRequestDTO,
)
from endpoints.instantiations.source_collector.meta_urls.post.dtos.response import (
    SourceCollectorMetaURLPostResponseDTO,
)
from endpoints.instantiations.source_collector.meta_urls.post.endpoint_schema_config import (
    SourceCollectorMetaURLPostEndpointSchemaConfig,
)
from middleware.enums import PermissionsEnum
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask


def test_source_collector_meta_urls_post(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask
    tdcdb = tdc.tdcdb
    tdc.clear_test_data()

    agency_ids = [int(tdcdb.agency().id) for _ in range(3)]

    tus_source_collector = tdc.user_with_permissions(
        permissions=[PermissionsEnum.SOURCE_COLLECTOR_DATA_SOURCES]
    )

    dto = SourceCollectorMetaURLPostRequestDTO(
        meta_urls=[
            SourceCollectorMetaURLPostRequestInnerDTO(
                agency_id=agency_ids[0],
                url="http://test.com",
            ),
            SourceCollectorMetaURLPostRequestInnerDTO(
                agency_id=agency_ids[1],
                url="http://test2.com",
            ),
            SourceCollectorMetaURLPostRequestInnerDTO(
                agency_id=agency_ids[2],
                url="http://test3.com",
            ),
        ]
    )

    response: dict = tdc.request_validator.post(
        endpoint="/source-collector/meta-urls",
        headers=tus_source_collector.jwt_authorization_header,
        json=dto.model_dump(mode="json"),
        expected_schema=SourceCollectorMetaURLPostEndpointSchemaConfig.primary_output_schema,
    )

    dto = SourceCollectorMetaURLPostResponseDTO(**response)
    assert len(dto.meta_urls) == 3

    meta_url_ids = [meta_url.meta_url_id for meta_url in dto.meta_urls]
    assert all(meta_url_id is not None for meta_url_id in meta_url_ids)

    meta_url_dbs: list[dict] = tdc.db_client.get_all(AgencyMetaURL)
    assert len(meta_url_dbs) == 3

    for meta_url_db in meta_url_dbs:
        assert meta_url_db["id"] in meta_url_ids
        assert meta_url_db["agency_id"] in agency_ids
        assert meta_url_db["url"] in {
            "http://test.com",
            "http://test2.com",
            "http://test3.com",
        }
