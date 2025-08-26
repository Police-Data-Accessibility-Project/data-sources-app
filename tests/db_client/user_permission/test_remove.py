from middleware.enums import PermissionsEnum
from tests.helpers.helper_functions_complex import create_test_user_db_client


def test_remove_user_permission(live_database_client):
    test_user = create_test_user_db_client(live_database_client)

    # Add permission
    live_database_client.add_user_permission(
        test_user.user_id, PermissionsEnum.READ_ALL_USER_INFO
    )
    test_user_permissions = live_database_client.get_user_permissions(test_user.user_id)
    assert len(test_user_permissions) == 1

    # Remove permission
    live_database_client.remove_user_permission(
        test_user.user_id, PermissionsEnum.READ_ALL_USER_INFO
    )
    test_user_permissions = live_database_client.get_user_permissions(test_user.user_id)
    assert len(test_user_permissions) == 0
