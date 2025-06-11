from db.models.implementations.link import LinkFollowRecordType
from middleware.enums import RecordTypes
from tests.integration.search.search_test_setup import SearchTestSetup
from utilities.enums import RecordCategories


def test_search_record_types(search_test_setup: SearchTestSetup):
    sts = search_test_setup
    tdc = sts.tdc
    rv = tdc.request_validator

    def check_record_type_count(expected_count: int):
        follows = tdc.db_client.get_all(LinkFollowRecordType)
        assert len(follows) == expected_count

    d = {
        RecordCategories.POLICE: [
            RecordTypes.ACCIDENT_REPORTS,
            RecordTypes.ARREST_RECORDS,
        ],
        RecordCategories.AGENCIES: [
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

    # Follow the same location again with a new category (3 record types)
    rv.follow_search(
        headers=sts.tus.jwt_authorization_header,
        location_id=sts.location_id,
        record_categories=[RecordCategories.JAIL],
    )

    # There should be 8 record types followed
    check_record_type_count(8)

    # Unfollow one location with an entire category
    rv.unfollow_search(
        headers=sts.tus.jwt_authorization_header,
        location_id=sts.location_id,
        record_categories=[RecordCategories.AGENCIES],
    )

    # Confirm those record types are no longer followed, while the other is unaffected
    # There should be 5 record types followed
    check_record_type_count(5)

    # Unfollow a single record type in the other category
    rv.unfollow_search(
        headers=sts.tus.jwt_authorization_header,
        location_id=sts.location_id,
        record_types=[RecordTypes.CONTACT_INFO_AGENCY_META],
    )

    # Confirm the remaining record types are still followed
    check_record_type_count(4)
