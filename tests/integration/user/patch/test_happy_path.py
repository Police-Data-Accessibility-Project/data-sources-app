from db.enums import UserCapacityEnum
from db.models.implementations.core.user.capacity import UserCapacity
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


def get_capacities_from_db(tdc, user_id: int):
    db_client = tdc.db_client
    result = db_client.get_all(UserCapacity)
    enum_results = []
    for r in result:
        if r["user_id"] == user_id:
            enum_results.append(UserCapacityEnum(r["capacity"]))
    return enum_results


def test_user_patch(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    tdc.clear_test_data()
    tus = tdc.standard_user()

    user_id = tus.user_info.user_id
    # Default test user capacities
    assert set(get_capacities_from_db(tdc, user_id)) == {
        UserCapacityEnum.POLICE,
        UserCapacityEnum.COMMUNITY_MEMBER,
    }

    tdc.request_validator.patch(
        endpoint=f"/api/user/{user_id}",
        headers=tus.jwt_authorization_header,
        json={
            "capacities": [
                UserCapacityEnum.POLICE.value,
                UserCapacityEnum.PUBLIC_OFFICIAL.value,
            ]
        },
    )

    # Check that entries present in database
    assert set(get_capacities_from_db(tdc, user_id)) == {
        UserCapacityEnum.POLICE,
        UserCapacityEnum.PUBLIC_OFFICIAL,
    }
