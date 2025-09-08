from endpoints.instantiations.source_collector.agencies.search.locations.dtos.request import \
    SourceCollectorAgencySearchLocationRequestDTO, SourceCollectorAgencySearchLocationRequestInnerDTO
from tests.helpers.helper_classes.RequestValidator import RequestValidator
from tests.helpers.helper_classes.test_data_creator.db_client_.core import TestDataCreatorDBClient
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask


def test_sc_agencies_search_location_happy_path(
    pittsburgh_id: int,
    allegheny_id: int,
    pennsylvania_id: int,
    test_data_creator_db_client: TestDataCreatorDBClient,
    test_data_creator_flask: TestDataCreatorFlask,

):
    tdc = test_data_creator_db_client
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
        # - One for "Pittsburgh, Allegheny, Pennsylvania'
        # - One for "Allegheny, Pennsylvania"
        # - One for "Pennsylvania"
    response = rv.post(
        "source-collector/agencies/search/location",
        headers=test_data_creator_flask.get_admin_tus().jwt_authorization_header,
        json=request.model_dump(mode="json")
    )

    # Confirm for each request, 3 agencies are returned

    # Confirm all three have the same agencies

    # Confirm that the highest for each request
    # is the agency linked to that location



