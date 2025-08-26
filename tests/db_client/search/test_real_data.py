from sqlalchemy.exc import IntegrityError

from db.enums import ApprovalStatus
from middleware.enums import RecordTypes
from tests.helpers.helper_classes.test_data_creator.db_client_.core import TestDataCreatorDBClient
from utilities.enums import RecordCategoryEnum


def test_search_with_location_and_record_types_real_data(
    test_data_creator_db_client: TestDataCreatorDBClient, live_database_client
):
    """
    Due to the large number of combinations, I will refer to tests using certain parameters by their first letter
    e.g. S=State, R=Record type, L=Locality, C=County
    In the absence of a large slew of test records, I will begin by testing that
    1) Each search returns a nonzero result count
    2) SRLC search returns the fewest results
    3) S search returns the most results
    4) SR returns less results than S but more than SRC
    5) SC returns less results than S but more than SCL
    :param live_database_client:
    :return:
    """
    state_parameter = "Pennsylvania"  # Additionally testing for case-insensitivity
    record_type_parameter = RecordCategoryEnum.AGENCIES
    county_parameter = "Allegheny"
    locality_parameter = "Pittsburgh"

    tdc = test_data_creator_db_client
    pennsylvania_location_id = live_database_client.get_location_id(
        where_mappings={"state_name": "Pennsylvania", "county_name": None}
    )
    allegheny_location_id = live_database_client.get_location_id(
        where_mappings={
            "state_name": "Pennsylvania",
            "county_name": "Allegheny",
            "locality_name": None,
        }
    )
    philadelphia_county_location_id = live_database_client.get_location_id(
        where_mappings={
            "state_name": "Pennsylvania",
            "county_name": "Philadelphia",
            "locality_name": None,
        }
    )
    try:
        pittsburgh_location_id = tdc.locality(locality_name="Pittsburgh")
    except IntegrityError:
        pittsburgh_location_id = tdc.db_client.get_location_id(
            where_mappings={
                "state_name": "Pennsylvania",
                "county_name": "Allegheny",
                "locality_name": "Pittsburgh",
            }
        )
    secondary_location_id = tdc.locality()

    def agency_and_data_source(
        location_id, record_type: RecordTypes = RecordTypes.LIST_OF_DATA_SOURCES
    ):
        ds_id = tdc.data_source(
            approval_status=ApprovalStatus.APPROVED, record_type=record_type
        ).id
        a_id = tdc.agency(location_id=location_id).id
        tdc.link_data_source_to_agency(data_source_id=ds_id, agency_id=a_id)

    # State
    agency_and_data_source(pennsylvania_location_id)
    agency_and_data_source(
        pennsylvania_location_id, record_type=RecordTypes.RECORDS_REQUEST_INFO
    )
    # Counties
    agency_and_data_source(allegheny_location_id)
    agency_and_data_source(philadelphia_county_location_id)
    # Localities
    agency_and_data_source(pittsburgh_location_id)
    agency_and_data_source(secondary_location_id)
    agency_and_data_source(
        pittsburgh_location_id, record_type=RecordTypes.RECORDS_REQUEST_INFO
    )

    def search(state, record_categories=None, county=None, locality=None):
        location_id = live_database_client.get_location_id(
            where_mappings={
                "state_name": state,
                "county_name": county,
                "locality_name": locality,
            }
        )
        if record_categories is not None:
            additional_kwargs = {"record_categories": record_categories}
        else:
            additional_kwargs = {}
        return live_database_client.search_with_location_and_record_type(
            location_id=location_id, **additional_kwargs
        )

    SRLC = len(
        search(
            state=state_parameter,
            record_categories=[record_type_parameter],
            county=county_parameter,
            locality=locality_parameter,
        )
    )
    S = len(search(state=state_parameter))
    SR = len(search(state=state_parameter, record_categories=[record_type_parameter]))
    SRC = len(
        search(
            state=state_parameter,
            record_categories=[record_type_parameter],
            county=county_parameter,
        )
    )
    SCL = len(
        search(
            state=state_parameter, county=county_parameter, locality=locality_parameter
        )
    )
    SC = len(search(state=state_parameter, county=county_parameter))

    assert SRLC > 0
    assert SRLC < SRC
    assert SRLC < SCL
    assert S > SR > SRC
    assert S > SC > SCL
