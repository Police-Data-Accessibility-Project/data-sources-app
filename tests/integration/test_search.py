from tests.helper_scripts.helper_functions import check_response_status
from tests.fixtures import client_with_db, bypass_api_required, dev_db_connection

def test_search_get(client_with_db, bypass_api_required):
    response = client_with_db.get("/search/search-location-and-record-type?state=Pennsylvania&county=Allegheny&locality=Pittsburgh&record_category=Police%20%26%20Public%20Interactions")
    check_response_status(response, 200)
    data = response.json

    assert data['count'] > 0
    assert list(data['data'][0].keys()) == ['agency_name', 'agency_supplied', 'coverage_end', 'coverage_start', 'data_source_name', 'description', 'format', 'id', 'municipality', 'record_type', 'state', 'url']

