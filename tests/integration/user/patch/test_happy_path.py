from db.enums import UserCapacityEnum
from db.models.implementations.core.user.capacity import UserCapacity
from tests.helper_scripts.helper_classes.test_data_creator.flask import TestDataCreatorFlask


def test_user_patch(
    test_data_creator_flask: TestDataCreatorFlask
):
    tdc = test_data_creator_flask
    tus = tdc.standard_user()
    tdc.request_validator.patch(
        endpoint=f"/api/user/{tus.user_info.user_id}",
        headers=tus.jwt_authorization_header,
        json={
            "capacities": [
                UserCapacityEnum.POLICE.value,
                UserCapacityEnum.PUBLIC_OFFICIAL.value,
            ]
        },
    )

    # Check that entries present in database
    db_client = tdc.db_client
    result = db_client.get_all(UserCapacity)
    assert len(result) == 2