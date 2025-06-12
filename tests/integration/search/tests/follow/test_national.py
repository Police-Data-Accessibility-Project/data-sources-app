from middleware.enums import RecordTypes
from tests.integration.search.search_test_setup import SearchTestSetup
from utilities.enums import RecordCategories


def test_search_national_follow(search_test_setup: SearchTestSetup):
    sts = search_test_setup
    tdc = sts.tdc
    tus = sts.tus
    rv = tdc.request_validator

    # Add national search with select record types
    rv.follow_national_search(
        headers=tus.jwt_authorization_header,
        record_types=[
            RecordTypes.INCARCERATION_RECORDS,
            RecordTypes.SEX_OFFENDER_REGISTRY,
        ],
    )

    # Get followed searches and confirm that national search is there,
    rv.get_followed_searches(
        headers=tus.jwt_authorization_header,
        expected_json_content={
            "metadata": {
                "count": 1,
            },
            "data": [
                {
                    "state_name": None,
                    "county_name": None,
                    "locality_name": None,
                    "display_name": "United States - All",
                    "location_id": tdc.db_client.get_national_location_id(),
                    "subscriptions_by_category": {
                        RecordCategories.JAIL.value: [
                            RecordTypes.INCARCERATION_RECORDS.value,
                        ],
                        RecordCategories.RESOURCE.value: [
                            RecordTypes.SEX_OFFENDER_REGISTRY.value,
                        ],
                    },
                }
            ],
            "message": "Followed searches found.",
        },
    )

    # Unfollow national search
    rv.unfollow_national_search(
        headers=tus.jwt_authorization_header,
    )

    # Get followed searches and confirm that national search is not there
    rv.get_followed_searches(
        headers=tus.jwt_authorization_header,
        expected_json_content={
            "metadata": {
                "count": 0,
            },
            "data": [],
            "message": "Followed searches found.",
        },
    )
