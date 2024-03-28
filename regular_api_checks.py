import os
import datetime
import json
import requests

API_KEY = os.getenv("VUE_APP_PDAP_API_KEY")
BASE_URL = os.getenv("VITE_VUE_API_BASE_URL")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}


# quick-search
def test_quicksearch_officer_involved_shootings_philadelphia_results():
    response = requests.get(
        f"{BASE_URL}/quick-search/Officer Involved Shootings/philadelphia",
        headers=HEADERS,
        json={"test_flag": True},
    )

    return len(response.json()["data"]) > 0


def test_quicksearch_officer_involved_shootings_lowercase_philadelphia_results():
    response = requests.get(
        f"{BASE_URL}/quick-search/officer involved shootings/Philadelphia",
        headers=HEADERS,
        json={"test_flag": True},
    )

    return len(response.json()["data"]) > 0


def test_quicksearch_officer_involved_shootings_philadelphia_county_results():
    response = requests.get(
        f"{BASE_URL}/quick-search/Officer Involved Shootings/philadelphia county",
        headers=HEADERS,
        json={"test_flag": True},
    )

    return len(response.json()["data"]) > 0


def test_quicksearch_all_allgeheny_results():
    response = requests.get(
        f"{BASE_URL}/quick-search/all/allegheny",
        headers=HEADERS,
        json={"test_flag": True},
    )

    return len(response.json()["data"]) > 0


def test_quicksearch_complaints_all_results():
    response = requests.get(
        f"{BASE_URL}/quick-search/complaints/all",
        headers=HEADERS,
        json={"test_flag": True},
    )

    return len(response.json()["data"]) > 0


def test_quicksearch_media_bulletin_pennsylvania_results():
    response = requests.get(
        f"{BASE_URL}/quick-search/media bulletin/pennsylvania",
        headers=HEADERS,
        json={"test_flag": True},
    )

    return len(response.json()["data"]) > 0


# data-sources
def test_data_source_by_id():
    response = requests.get(
        f"{BASE_URL}/data-sources-by-id/reczwxaH31Wf9gRjS",
        headers=HEADERS,
    )

    return len(response.json()["data"]) > 0


def test_data_sources():
    response = requests.get(f"{BASE_URL}/data-sources", headers=HEADERS)

    return len(response.json()["data"]) > 0


def test_create_data_source():
    response = requests.post(
        f"{BASE_URL}/data-sources",
        headers=HEADERS,
        json={"name": "test", "record_type": "test"},
    )

    assert response.json() == True


def test_update_data_source():
    response = requests.put(
        f"{BASE_URL}/data-sources-by-id/45a4cd5d-26da-473a-a98e-a39fbcf4a96c",
        headers=HEADERS,
        json={"description": "test"},
    )

    assert response.json()["message"] == "Data source updated successfully."


def test_data_sources_approved():
    response = requests.get(f"{BASE_URL}/data-sources", headers=HEADERS)
    unapproved_url = "https://joinstatepolice.ny.gov/15-mile-run"

    return (
        len([d for d in response.json()["data"] if d["source_url"] == unapproved_url])
        == 0
    )


def test_data_source_by_id_approved():
    response = requests.get(
        f"{BASE_URL}/data-sources-by-id/rec013MFNfBnrTpZj",
        headers=HEADERS,
    )

    return response.json() == "Data source not found."


# search-tokens
def test_search_tokens_data_sources():
    response = requests.get(f"{BASE_URL}/search-tokens?endpoint=data-sources")

    return len(response.json()["data"]) > 0


def test_search_tokens_data_source_by_id():
    response = requests.get(
        f"{BASE_URL}/search-tokens?endpoint=data-sources-by-id&arg1=reczwxaH31Wf9gRjS"
    )

    return response.json()["data_source_id"] == "reczwxaH31Wf9gRjS"


def test_search_tokens_quick_search_complaints_allegheny_results():
    response = requests.get(
        f"{BASE_URL}/search-tokens?endpoint=quick-search&arg1=complaints&arg2=allegheny"
    )

    return len(response.json()["data"]) > 0


# user
def test_put_user():
    response = requests.put(
        f"{BASE_URL}/user",
        headers=HEADERS,
        json={"email": "test2", "password": "test"},
    )

    return response.json()["message"] == "Successfully updated password"


# login
def test_login():
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": "test2", "password": "test"},
    )

    return response.json()["message"] == "Successfully logged in"


# refresh-session
def test_refresh_session():
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": "test2", "password": "test"},
    )
    token = response.json()["data"]

    response = requests.post(
        f"{BASE_URL}/refresh-session", json={"session_token": token}
    )

    return response.json()["message"] == "Successfully refreshed session token"


# reset-password
def test_request_reset_password():
    reset_token = requests.post(
        f"{BASE_URL}/request-reset-password",
        headers=HEADERS,
        json={"email": "test"},
    )

    response = requests.post(
        f"{BASE_URL}/reset-password",
        headers=HEADERS,
        json={"token": reset_token.json()["token"], "password": "test"},
    )

    return response.json()["message"] == "Successfully updated password"


def test_reset_token_validation():
    reset_token = requests.post(
        f"{BASE_URL}/request-reset-password",
        headers=HEADERS,
        json={"email": "test2"},
    )

    response = requests.post(
        f"{BASE_URL}/reset-token-validation",
        headers=HEADERS,
        json={"token": reset_token.json()["token"], "password": "test"},
    )

    return response.json()["message"] == "Token is valid"


# api-key
def test_get_api_key():
    response = requests.get(
        f"{BASE_URL}/api_key",
        headers=HEADERS,
        json={"email": "test2", "password": "test"},
    )

    return len(response.json()["api_key"]) > 0


# archives
def test_get_archives():
    response = requests.get(f"{BASE_URL}/archives", headers=HEADERS)

    return len(response.json()[0]) > 0


def test_put_archives():
    current_datetime = datetime.datetime.now()
    datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    response = requests.put(
        f"{BASE_URL}/archives",
        headers=HEADERS,
        json=json.dumps(
            {
                "id": "45a4cd5d-26da-473a-a98e-a39fbcf4a96c",
                "last_cached": datetime_string,
                "broken_source_url_as_of": "",
            }
        ),
    )

    return response.json()["status"] == "success"


def test_put_archives_brokenasof():
    current_datetime = datetime.datetime.now()
    datetime_string = current_datetime.strftime("%Y-%m-%d")
    response = requests.put(
        f"{BASE_URL}/archives",
        headers=HEADERS,
        json=json.dumps(
            {
                "id": "45a4cd5d-26da-473a-a98e-a39fbcf4a96c",
                "last_cached": datetime_string,
                "broken_source_url_as_of": datetime_string,
            }
        ),
    )

    return response.json()["status"] == "success"


# agencies
def test_agencies():
    response = requests.get(f"{BASE_URL}/agencies/1", headers=HEADERS)

    return len(response.json()["data"]) > 0


def test_agencies_pagination():
    response1 = requests.get(f"{BASE_URL}/agencies/1", headers=HEADERS)
    response2 = requests.get(f"{BASE_URL}/agencies/2", headers=HEADERS)

    return response1 != response2


def main():
    tests = [
        "test_quicksearch_officer_involved_shootings_philadelphia_results",
        "test_quicksearch_officer_involved_shootings_lowercase_philadelphia_results",
        "test_quicksearch_officer_involved_shootings_philadelphia_county_results",
        "test_quicksearch_all_allgeheny_results",
        "test_quicksearch_complaints_all_results",
        "test_quicksearch_media_bulletin_pennsylvania_results",
        "test_data_source_by_id",
        "test_data_sources",
        "test_update_data_source",
        "test_data_sources_approved",
        "test_data_source_by_id_approved",
        "test_search_tokens_data_sources",
        "test_search_tokens_data_source_by_id",
        "test_search_tokens_quick_search_complaints_allegheny_results",
        "test_put_user",
        "test_login",
        "test_request_reset_password",
        "test_get_api_key",
        "test_get_archives",
        "test_put_archives",
        "test_put_archives_brokenasof",
        "test_agencies",
        "test_agencies_pagination",
    ]

    fails = []
    for test in tests:
        print(f"Running test {test}...")
        if eval(f"{test}()") == True:
            print(f"Test {test} passed.")
        else:
            print(f"Test {test} failed.")
            fails.append(test)

    return fails


if __name__ == "__main__":
    print(main())
