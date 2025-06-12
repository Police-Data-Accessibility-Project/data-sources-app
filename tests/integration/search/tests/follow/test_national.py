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
        headers=tus.api_authorization_header,
        location_id=sts.location_id,
        record_types=[
            RecordTypes.INCARCERATION_RECORDS,
            RecordTypes.SEX_OFFENDER_REGISTRY,
        ],
    )

    # Get followed searches and confirm that national search is there,
    ...

    # Unfollow national search
    rv.unfollow_national_search(
        headers=tus.api_authorization_header,
        location_id=sts.location_id,
    )

    # Get followed searches and confirm that national search is not there
    ...
