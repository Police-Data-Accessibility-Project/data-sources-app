from tests.helpers.helper_functions_complex import create_test_user_db_client


def test_get_user_permissions_default(live_database_client):
    test_user = create_test_user_db_client(live_database_client)
    test_user_permissions = live_database_client.get_user_permissions(test_user.user_id)
    assert len(test_user_permissions) == 0
