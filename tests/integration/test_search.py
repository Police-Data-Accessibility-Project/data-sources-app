from tests.helper_functions import check_response_status
from tests.fixtures import client_with_db, dev_db_connection, bypass_api_required

def test_search_get(client_with_db, bypass_api_required):
    response = client_with_db.get("/search?state=Pennsylvania&county=Allegheny&locality=Pittsburgh&record_category=Police%20%26%20Public%20Interactions")
    check_response_status(response, 200)
    data = response.json

    assert len(data) > 0
    assert list(data[0].keys()) == ['agency_name', 'agency_supplied', 'coverage_end', 'coverage_start', 'data_source_name', 'description', 'format', 'id', 'municipality', 'record_type', 'state', 'url']

