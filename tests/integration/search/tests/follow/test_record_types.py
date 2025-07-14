from db.enums import LocationType
from db.helpers_.result_formatting import get_display_name
from db.models.implementations.link import LinkFollowRecordType
from middleware.enums import RecordTypes
from tests.integration.search.constants import TEST_STATE, TEST_COUNTY, TEST_LOCALITY
from tests.integration.search.search_test_setup import SearchTestSetup
from utilities.enums import RecordCategoryEnum


def test_search_record_types(search_test_setup: SearchTestSetup):
    sts = search_test_setup
    tdc = sts.tdc
    rv = tdc.request_validator

    def check_result(
        expected_record_categories_dict: dict,
    ):
        return rv.get_followed_searches(
            headers=sts.tus.jwt_authorization_header,
            expected_json_content={
                "metadata": {
                    "count": 1,
                },
                "data": [
                    {
                        "state_name": TEST_STATE,
                        "county_name": TEST_COUNTY,
                        "locality_name": TEST_LOCALITY,
                        "display_name": get_display_name(
                            location_type=LocationType.LOCALITY,
                            state_name=TEST_STATE,
                            county_name=TEST_COUNTY,
                            locality_name=TEST_LOCALITY,
                        ),
                        "location_id": sts.location_id,
                        "subscriptions_by_category": expected_record_categories_dict,
                    }
                ],
                "message": "Followed searches found.",
            },
        )

    d = {
        RecordCategoryEnum.POLICE: [
            RecordTypes.ACCIDENT_REPORTS,
            RecordTypes.ARREST_RECORDS,
        ],
        RecordCategoryEnum.AGENCIES: [
            RecordTypes.ANNUAL_MONTHLY_REPORTS,
            RecordTypes.BUDGETS_FINANCES,
            RecordTypes.CONTACT_INFO_AGENCY_META,
        ],
    }
    record_types = []
    for category in d:
        for record_type in d[category]:
            record_types.append(record_type)
    # Follow one location with selected record types across two categories
    rv.follow_search(
        headers=sts.tus.jwt_authorization_header,
        location_id=sts.location_id,
        record_types=record_types,
    )

    check_result(
        {
            RecordCategoryEnum.POLICE.value: [
                RecordTypes.ACCIDENT_REPORTS.value,
                RecordTypes.ARREST_RECORDS.value,
            ],
            RecordCategoryEnum.AGENCIES.value: [
                RecordTypes.ANNUAL_MONTHLY_REPORTS.value,
                RecordTypes.BUDGETS_FINANCES.value,
                RecordTypes.CONTACT_INFO_AGENCY_META.value,
            ],
        }
    )

    # Follow the same location again with a new category (3 record types)
    rv.follow_search(
        headers=sts.tus.jwt_authorization_header,
        location_id=sts.location_id,
        record_categories=[RecordCategoryEnum.JAIL],
    )

    # There should be 8 record types followed
    check_result(
        {
            RecordCategoryEnum.POLICE.value: [
                RecordTypes.ACCIDENT_REPORTS.value,
                RecordTypes.ARREST_RECORDS.value,
            ],
            RecordCategoryEnum.AGENCIES.value: [
                RecordTypes.ANNUAL_MONTHLY_REPORTS.value,
                RecordTypes.BUDGETS_FINANCES.value,
                RecordTypes.CONTACT_INFO_AGENCY_META.value,
            ],
            RecordCategoryEnum.JAIL.value: [
                RecordTypes.BOOKING_REPORTS.value,
                RecordTypes.COURT_CASES.value,
                RecordTypes.INCARCERATION_RECORDS.value,
            ],
        }
    )

    # Unfollow one location with an entire category
    rv.unfollow_search(
        headers=sts.tus.jwt_authorization_header,
        location_id=sts.location_id,
        record_categories=[RecordCategoryEnum.AGENCIES],
    )

    # Confirm those record types are no longer followed, while the other is unaffected
    # There should be 5 record types followed
    check_result(
        {
            RecordCategoryEnum.POLICE.value: [
                RecordTypes.ACCIDENT_REPORTS.value,
                RecordTypes.ARREST_RECORDS.value,
            ],
            RecordCategoryEnum.JAIL.value: [
                RecordTypes.BOOKING_REPORTS.value,
                RecordTypes.COURT_CASES.value,
                RecordTypes.INCARCERATION_RECORDS.value,
            ],
        }
    )

    # Unfollow a single record type in the other category
    rv.unfollow_search(
        headers=sts.tus.jwt_authorization_header,
        location_id=sts.location_id,
        record_types=[RecordTypes.ACCIDENT_REPORTS],
    )

    # Confirm the remaining record types are still followed
    check_result(
        {
            RecordCategoryEnum.POLICE.value: [
                RecordTypes.ARREST_RECORDS.value,
            ],
            RecordCategoryEnum.JAIL.value: [
                RecordTypes.BOOKING_REPORTS.value,
                RecordTypes.COURT_CASES.value,
                RecordTypes.INCARCERATION_RECORDS.value,
            ],
        }
    )

    # Follow the entire location and confirm all record types are followed
    rv.follow_search(
        headers=sts.tus.jwt_authorization_header,
        location_id=sts.location_id,
    )

    # There should be 36 record types followed
    follows = tdc.db_client.get_all(LinkFollowRecordType)
    assert len(follows) == 36
