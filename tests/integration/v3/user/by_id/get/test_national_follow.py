from endpoints.v3.user.by_id.get.response.core import GetUserProfileResponse
from tests.helpers.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)
from tests.helpers.test_dataclasses import TestUserDBInfo
from tests.integration.v3.helpers.api_test_helper import APITestHelper


def test_national_follow(
    test_data_creator_db_client: TestDataCreatorDBClient,
    api_test_helper: APITestHelper,
    national_id: int,
    monkeypatch,
):
    tdc = test_data_creator_db_client
    tus: TestUserDBInfo = tdc.user()

    # Add national search follow
    test_data_creator_db_client.db_client.create_followed_search(
        user_id=tus.id,
        location_id=national_id,
    )

    # Call user profile endpoint and confirm it returns results
    monkeypatch.setattr(
        "endpoints.v3.user.by_id.get.wrapper._check_user_is_either_owner_or_admin",
        lambda x, user_id: None,
    )
    json: dict = api_test_helper.request_validator.get_v3(f"/user/{tus.id}")
    model = GetUserProfileResponse(**json)

    assert len(model.followed_searches[0].record_categories) == 6
