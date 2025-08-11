from db.client.core import DatabaseClient
from endpoints.instantiations.map.data.wrapper import get_data_for_map_wrapper
from middleware.util.env import get_env_variable


def test_data_map(
    monkeypatch,
):
    monkeypatch.setenv("DO_DATABASE_URL", get_env_variable("PROD_DATABASE_URL"))

    response = get_data_for_map_wrapper(db_client=DatabaseClient())
    print(response)
