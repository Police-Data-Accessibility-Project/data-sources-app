from db.client.core import DatabaseClient
from middleware.primary_resource_logic.notifications.notifications import (
    preview_notifications,
)
from middleware.util.env import get_env_variable


def test_notifications_preview(
    monkeypatch,
):
    monkeypatch.setenv("DO_DATABASE_URL", get_env_variable("PROD_DATABASE_URL"))

    response = preview_notifications(db_client=DatabaseClient(), access_info=None)
    print(response)
