import datetime
from unittest.mock import MagicMock
from venv import create

import pytest
from port_for.docopt import Optional

from database_client.enums import LocationType, RequestStatus
from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from tests.helper_scripts.common_test_data import TestDataCreatorFlask
from tests.helper_scripts.helper_classes.TestDataCreatorDBClient import TestDataCreatorDBClient
from conftest import test_data_creator_flask, monkeysession
from tests.helper_scripts.helper_classes.EndpointCaller import EndpointCallInfo
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.helper_functions import add_query_params
from tests.helper_scripts.run_and_validate_request import run_and_validate_request

PITTSBURGH_LOCATION_INFO = {
    "type": LocationType.LOCALITY.value,
    "state_iso": "PA",
    "county_fips": "42003",
    "locality_name": "Pittsburgh",
}

OHIO_LOCATION_INFO = {
    "type": LocationType.STATE.value,
    "state_iso": "OH",
}

ORANGE_COUNTY_LOCATION_INFO = {
    "type": LocationType.COUNTY.value,
    "state_iso": "CA",
    "county_fips": "06059",
}



def test_notifications_followed_searches(
        test_data_creator_flask: TestDataCreatorFlask,
        monkeypatch
):
    datetime_two_months_ago = datetime.datetime.now() - datetime.timedelta(days=60)

    tdc = test_data_creator_flask
    tdc_db = TestDataCreatorDBClient()

    # Create agency and tie to location (Pittsburgh)
    agency_info = tdc.agency(location_info=PITTSBURGH_LOCATION_INFO)

    # Create data source with approval status of "approved" and associate with agency
    ds_info = tdc.data_source()

    tdc.link_data_source_to_agency(
        data_source_id=ds_info.id,
        agency_id=agency_info.id,
    )

    # Create data request with request_status of `Active` and associate with location 'Ohio'
    def create_test_notification_data_request(
        location_info: dict,
        status: RequestStatus,
        status_updated_at: Optional[datetime] = None
    ):
        dr_info = tdc.data_request(
            location_info=location_info
        )
        update_mappings = {
            "request_status": status.value
        }
        if status_updated_at is not None:
            update_mappings["status_updated_at"] = status_updated_at

        tdc.db_client.update_data_request(
            entry_id=dr_info.id,
            column_edit_mappings=update_mappings
        )
        return dr_info
    dr_info_active_ohio = create_test_notification_data_request(
        location_info=OHIO_LOCATION_INFO,
        status=RequestStatus.ACTIVE,
    )

    # Create data request with request_status of `Complete` and associate with location 'Orange County, California'
    dr_info_complete_orange_county = create_test_notification_data_request(
        location_info=ORANGE_COUNTY_LOCATION_INFO,
        status=RequestStatus.COMPLETE,
    )

    # For all of the above, create additional data with the above parameters
    # but manipulate their `status_updated_at` columns to be prior to a month ago.
    # This data should not be included in the final result


    ds_info_not_included = tdc.data_source()
    tdc.link_data_source_to_agency(
        data_source_id=ds_info_not_included.id,
        agency_id=agency_info.id,
    )
    tdc_db.update_data_source(
        data_source_id=ds_info_not_included.id,
        column_value_mappings={
            "status_updated_at": datetime_two_months_ago
        }
    )

    dr_info_active_ohio_not_included = create_test_notification_data_request(
        location_info=OHIO_LOCATION_INFO,
        status=RequestStatus.ACTIVE,
        status_updated_at=datetime_two_months_ago
    )



    dr_info_complete_orange_county_not_included = create_test_notification_data_request(
        location_info=ORANGE_COUNTY_LOCATION_INFO,
        status=RequestStatus.COMPLETE,
        status_updated_at=datetime_two_months_ago
    )

    # Create additional requests and data sources associated with locations not included in the above

    # Create user and have them follow
    tus_1: TestUserSetup = tdc.standard_user()
    # Pittsburgh
    # Cleveland Ohio
    # Orange County, California

    def follow_location(user_info: TestUserSetup, location_info: dict):
        param_dict = {
            "state": location_info["state_iso"]
        }
        if "county_fips" in location_info:
            param_dict["county"] = location_info["county_fips"]
        if "locality_name" in location_info:
            param_dict["locality"] = location_info["locality_name"]

        tdc.endpoint_caller.follow_location(
            eci=EndpointCallInfo(
                authorization_header=user_info.jwt_authorization_header,
                expected_json_content={
                    "message": "Location successfully followed"
                },
                query_parameters=param_dict
            )
        )


    for location in [PITTSBURGH_LOCATION_INFO, OHIO_LOCATION_INFO, ORANGE_COUNTY_LOCATION_INFO]:
        follow_location(user_info=tus_1, location_info=location)

    # Create a different user and have them follow a different location
    # which has no triggering data; they should not receive any notifications
    tus_2: TestUserSetup = tdc.standard_user()

    follow_location(user_info=tus_2, location_info={
        "type": LocationType.STATE.value,
        "state_iso": "WA",
    })

    # patch "format_and_send_notification" function
    mock_format_and_send_notification = MagicMock()
    monkeypatch.setattr(
        f"{PATCH_ROOT}.format_and_send_notification",
        mock_format_and_send_notification
    )

    # Call the notifications endpoint and confirm it returns a 200 status
    # With a message "Notifications sent successfully"

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=NOTIFICATIONS_ENDPOINT,
        headers=tus_1.jwt_authorization_header,
        expected_json_content={"message": "Notifications sent successfully"},
        expected_schema=MessageSchema
    )

    # Test that it calls the `format_and_send_notification` function with the requisite results, and only once

    pytest.fail("Not implemented yet")

    # mock_format_and_send_notification.assert_called_once_with(
    #
    # )
    # TODO: Create separate middleware test for `format_and_send_notification`

def test_notifications_permission_denied():
    """
    Test that for basic admins and standard users, they are not able to call the endpoint
    """
    pytest.fail("Not implemented yet")