from db.client.core import DatabaseClient
from endpoints.instantiations.source_collector.agencies.search.locations.dtos.request import \
    SourceCollectorAgencySearchLocationRequestDTO, SourceCollectorAgencySearchLocationRequestInnerDTO
from endpoints.instantiations.source_collector.agencies.search.locations.dtos.response import \
    SourceCollectorAgencySearchLocationResponseDTO, InnerSearchLocationResponse, SearchLocationRequestResponse
from endpoints.instantiations.source_collector.agencies.search.locations.schemas.response import \
    SourceCollectorAgencySearchLocationResponseSchema
from tests.helpers.helper_classes.RequestValidator import RequestValidator
from tests.helpers.helper_classes.test_data_creator.db_client_.core import TestDataCreatorDBClient
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask


def test_sc_agencies_search_location_happy_path(
    test_data_creator_db_client: TestDataCreatorDBClient,
    test_data_creator_flask: TestDataCreatorFlask,
    pittsburgh_id: int,
    allegheny_id: int,
    pennsylvania_id: int,
):
    tdc = test_data_creator_db_client
    tdc.db_client.refresh_all_materialized_views()
    rv: RequestValidator = test_data_creator_flask.request_validator
    # Create three agencies

    # Link agency to Pittsburgh, PA
    pittsburgh_agency_id: int = tdc.agency(location_id=pittsburgh_id).id

    # Link agency to Allegheny, PA
    allegheny_agency_id: int = tdc.agency(location_id=allegheny_id).id

    # Link agency to Pennsylvania
    pennsylvania_agency_id: int = tdc.agency(location_id=pennsylvania_id).id



    # Run request
    request = SourceCollectorAgencySearchLocationRequestDTO(
        requests=[
            SourceCollectorAgencySearchLocationRequestInnerDTO(
                query="Pittsburgh, Allegheny, Pennsylvania",
                request_id=1
            ),
            SourceCollectorAgencySearchLocationRequestInnerDTO(
                query="Allegheny, Pennsylvania",
                request_id=2
            ),
            SourceCollectorAgencySearchLocationRequestInnerDTO(
                query="Pennsylvania",
                request_id=3
            ),
        ]
    )
    # Include three searches.
        # - One for "Pittsburgh, Allegheny, Pennsylvania"
        # - One for "Allegheny, Pennsylvania"
        # - One for "Pennsylvania"
    request_response: dict = rv.post(
        "source-collector/agencies/search/location",
        headers=test_data_creator_flask.get_admin_tus().jwt_authorization_header,
        json=request.model_dump(mode="json"),
        expected_schema=SourceCollectorAgencySearchLocationResponseSchema
    )
    dto = SourceCollectorAgencySearchLocationResponseDTO(**request_response)

    # Confirm for each request, 3 agencies are returned
    assert len(dto.responses) == 3
    request_id_to_results: dict[int, list[InnerSearchLocationResponse]] = {}
    for response in dto.responses:
        assert len(response.results) == 3
        request_id_to_results[response.request_id] = response.results

    # Confirm all three have the same agencies
    results_1: list[InnerSearchLocationResponse] = request_id_to_results[1]
    results_2: list[InnerSearchLocationResponse] = request_id_to_results[2]
    results_3: list[InnerSearchLocationResponse] = request_id_to_results[3]

    agencies_1: set[int] = {result.agency_id for result in results_1}
    agencies_2: set[int] = {result.agency_id for result in results_2}
    agencies_3: set[int] = {result.agency_id for result in results_3}

    assert agencies_1 == agencies_2 == agencies_3

    # Confirm that the highest for each request
    max_similarity_agency_1: int = max(results_1, key=lambda result: result.similarity).agency_id
    max_similarity_agency_2: int = max(results_2, key=lambda result: result.similarity).agency_id
    max_similarity_agency_3: int = max(results_3, key=lambda result: result.similarity).agency_id
    # is the agency linked to that location
    assert max_similarity_agency_1 == pittsburgh_agency_id
    assert max_similarity_agency_2 == allegheny_agency_id
    assert max_similarity_agency_3 == pennsylvania_agency_id




