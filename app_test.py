import pytest
import os
from app import app
from flask_restful import Api
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection
from middleware.quick_search_query import QUICK_SEARCH_TEST_SQL
from middleware.data_source_queries import APPROVED_COLUMNS
import datetime
import json
import psycopg2
import sqlite3

api_key = os.getenv("VUE_APP_PDAP_API_KEY")
HEADERS = {"Authorization": f"Bearer {api_key}"}
current_datetime = datetime.datetime.now()
DATETIME_STRING = current_datetime.strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture()
def test_app():
    yield app


@pytest.fixture()
def client(test_app):
    return test_app.test_client()


@pytest.fixture()
def runner(test_app):
    return test_app.test_cli_runner()


@pytest.fixture
def session():
    connection = sqlite3.connect("file::memory:?cache=shared", uri=True)
    db_session = connection.cursor()
    with open("do_db_ddl_clean.sql", "r") as f:
        sql_file = f.read()
        sql_queries = sql_file.split(";")
        for query in sql_queries:
            db_session.execute(query.replace("\n", ""))

    data_source_rows = [
        {
            "airtable_uid": "rec00T2YLS2jU7Tbn",
            "name": "Calls for Service for Chicago Police Department - IL",
            "description": None,
            "record_type": "Calls for Service",
            "source_url": "https://informationportal.igchicago.org/911-calls-for-cpd-service/",
            "record_format": None,
            "coverage_start": "2019-01-01",
            "coverage_end": None,
            "agency_supplied": True,
            "agency_name": "Chicago Police Department - IL",
            "municipality": "Chicago",
            "state_iso": "IL",
        },
        {
            "airtable_uid": "recUGIoPQbJ6laBmr",
            "data_source_name": "311 Calls for City of Chicago",
            "description": "311 Service Requests received by the City of Chicago. This dataset includes requests created after the launch of the new 311 system on 12/18/2018 and some records from the previous system, indicated in the LEGACY\\_RECORD column.\n\nIncluded as a Data Source because in some cities 311 calls lead to police response; that does not appear to be the case in Chicago.\n",
            "record_type": "Calls for Service",
            "source_url": "https://data.cityofchicago.org/Service-Requests/311-Service-Requests/v6vf-nfxy",
            "record_format": ["CSV", "XML", "RDF", "RSS"],
            "coverage_start": "2018-12-18",
            "coverage_end": None,
            "agency_supplied": False,
            "agency_name": "Chicago Police Department - IL",
            "municipality": "Chicago",
            "state_iso": "IL",
        },
    ]
    all_columns = APPROVED_COLUMNS + ["airtable_uid"]
    valid_row = {k: v for k, v in data_source_rows[0].items() if k in all_columns}
    clean_row = [r if r is not None else "" for r in valid_row.values()]
    fully_clean_row = [r if r is not True else "True" for r in clean_row]
    fully_clean_row_str = "'" + "', '".join(fully_clean_row) + "'"
    col_str = ", ".join(valid_row.keys())
    db_session.execute(
        f"insert into data_sources ({col_str}) values ({fully_clean_row_str})"
    )

    agency_link_rows = [("rec00T2YLS2jU7Tbn", "recv9fMNEQTbVarj2")]
    db_session.execute(
        f"insert into agency_source_link (link_id, airtable_uid, agency_described_linked_uid) values (1, 'rec00T2YLS2jU7Tbn', 'recv9fMNEQTbVarj2')"
    )

    agencies_rows = [
        (
            "Chicago Police Department - IL",
            "Chicago Police Department",
            "https://home.chicagopolice.org/",
            "local",
            "IL",
            "Chicago",
            "17031",
            '["Cook"]',
            41.85861,
            -87.62802,
            None,
            "recv9fMNEQTbVarj2",
            21,
            "law enforcement/police",
            None,
            "60616",
            '["recs7gYAGAMWEhLYC", "recyR4IVgqyIekzYB", "recBMxu4UcHCqjsWQ", "recqXzWtmhfV9z8Av", "recc5QWeCMGL17Ab6", "recD9bNxneanhBBDH", "recPUGM4OEopoRAXB", "rec10Mts7CmMPzcnx", "recTj2zTdu7Jp8oX9", "rec00T2YLS2jU7Tbn", "recpOsfsTV4bKmVfa", "recipwTdMN0jRADrt", "recjFk7X0KofjTPGK", "rec0Lqwrj6blSbkuz", "recYyAY8XVQJJVde6", "recgwPuRTwjAMUZeO", "recOLt1yQGlgrO5jQ", "recdAte1fo5FBruE7", "recUGIoPQbJ6laBmr", "recTw75rItd827L0r", "rechI06qD4od759xT", "recodGxvuxiTXPnOL"]',
            None,
            datetime.datetime(2023, 5, 16, 17, 37, 6, tzinfo=datetime.timezone.utc),
            datetime.date(2023, 4, 6),
            True,
            None,
            '{"id": "usrtLIB4Vr3jTH8Ro", "email": "josh.chamberlain@pdap.io", "name": "Josh Chamberlain"}',
            None,
            datetime.datetime(2022, 8, 18, 18, 50, 7, tzinfo=datetime.timezone.utc),
            "recuhY2ud60V41j0w",
        )
    ]
    clean_row = [r if r is not None else "" for r in agencies_rows[0]]
    fully_clean_row = [
        str(r) for r in clean_row
    ]  # if r is not True else 'True' for r in clean_row]
    fully_clean_row_str = "'" + "', '".join(fully_clean_row) + "'"

    db_session.execute(f"insert into agencies values ({fully_clean_row_str})")
    db_session.execute(f"insert into state_names values (1, 'IL', 'Illinois')")

    sql_query_log = f"INSERT INTO quick_search_query_logs (id, search, location, results, result_count, datetime_of_request, created_at) VALUES (1, 'test', 'test', '', 0, '{DATETIME_STRING}', '{DATETIME_STRING}')"
    db_session.execute(sql_query_log)

    yield db_session
    connection.close()


# @pytest.fixture
# def setup_db(session):


# unit tests
def test_psycopg2_connection(client):
    with initialize_psycopg2_connection() as psycopg2_connection:
        assert type(psycopg2_connection) != dict


def test_quick_search_query(session):
    # with initialize_psycopg2_connection() as psycopg2_connection:
    #     cursor = psycopg2_connection.cursor()
    session.execute("select * from data_sources")  # QUICK_SEARCH_TEST_SQL)
    results = session.fetchall()
    print(results)

    assert len(results) > 0


def test_quick_search_logging(session):
    session.execute(
        f"SELECT * FROM quick_search_query_logs WHERE datetime_of_request = '{DATETIME_STRING}'"
    )
    results = session.fetchall()

    assert len(results) > 0


# # quick-search
# def test_quicksearch_complaints_allegheny_results(client):
#
#     response = client.get("/quick-search/complaints/allegheny", headers=headers)

#     assert len(response.json["data"]) > 0


# def test_quicksearch_columns(client):
#     response = client.get("/quick-search/complaints/allegheny", headers=HEADERS)
#     column_names = [
#         "airtable_uid",
#         "data_source_name",
#         "record_type",
#         "source_url",
#         "record_format",
#         "coverage_start",
#         "coverage_end",
#         "agency_name",
#         "municipality",
#         "state_iso",
#     ]

#     assert not set(column_names).difference(response.json["data"][0].keys())


# def test_quicksearch_complaints_allegheny_county_results(client):
#     response = client.get("/quick-search/complaints/allegheny county", headers=HEADERS)

#     assert len(response.json["data"]) > 0


# def test_quicksearch_officer_involved_shootings_philadelphia_results(client):
#     response = client.get(
#         "/quick-search/Officer Involved Shootings/philadelphia", headers=HEADERS
#     )

#     assert len(response.json["data"]) > 0


# def test_quicksearch_officer_involved_shootings_philadelphia_county_results(client):
#     response = client.get(
#         "/quick-search/Officer Involved Shootings/philadelphia county", headers=HEADERS
#     )

#     assert len(response.json["data"]) > 0


# def test_quicksearch_officer_involved_shootings_kings_results(client):
#     response = client.get(
#         "/quick-search/Officer Involved Shootings/kings", headers=HEADERS
#     )

#     assert len(response.json["data"]) > 0


# def test_quicksearch_officer_involved_shootings_kings_county_results(client):
#     response = client.get(
#         "/quick-search/Officer Involved Shootings/kings county", headers=HEADERS
#     )

#     assert len(response.json["data"]) > 0


# def test_quicksearch_all_allgeheny_results(client):
#     response = client.get("/quick-search/all/allegheny", headers=HEADERS)

#     assert len(response.json["data"]) > 0


# def test_quicksearch_complaints_all_results(client):
#     response = client.get("/quick-search/complaints/all", headers=HEADERS)

#     assert len(response.json["data"]) > 0


# def test_quicksearch_media_bulletin_pennsylvania_results(client):
#     response = client.get("/quick-search/media bulletin/pennsylvania", headers=HEADERS)

#     assert len(response.json["data"]) > 0


# def test_quicksearch_officer_involved_shootings_philadelphia_results(client):
#     response = client.get(
#         "/quick-search/officer involved shootings/Philadelphia", headers=HEADERS
#     )

#     assert len(response.json["data"]) > 0


# def test_quicksearch_format_available_formatting(client):
#     response = client.get("/quick-search/reviews/allegheny", headers=HEADERS)

#     assert type(response.json["data"][0]["record_format"]) == list


# # data-sources
# def test_data_source_by_id(client):
#     response = client.get("/data-sources-by-id/reczwxaH31Wf9gRjS", headers=HEADERS)

#     assert response.json["data_source_id"] == "reczwxaH31Wf9gRjS"


# def test_data_source_by_id_columns(client):
#     response = client.get("/data-sources-by-id/reczwxaH31Wf9gRjS", headers=HEADERS)
#     column_names = [
#         "description",
#         "record_type",
#         "agency_name",
#         "state_iso",
#         "county_name",
#         "municipality",
#         "agency_type",
#         "jurisdiction_type",
#         "source_url",
#         "readme_url",
#         "access_type",
#         "record_format",
#         "detail_level",
#         "size",
#         "access_type",
#         "access_notes",
#         "records_not_online",
#         "agency_supplied",
#         "supplying_entity",
#         "agency_originated",
#         "originating_entity",
#         "coverage_start",
#         "coverage_end",
#         "source_last_updated",
#         "update_frequency",
#         "update_method",
#         "retention_schedule",
#         "number_of_records_available",
#         "scraper_url",
#         "data_source_created",
#         "data_source_id",
#         "agency_id",
#     ]

#     assert not set(column_names).difference(response.json.keys())


# def test_data_sources(client):
#     response = client.get("/data-sources", headers=HEADERS)

#     assert len(response.json["data"]) > 0


# def test_data_sources_approved(client):
#     response = client.get("/data-sources", headers=HEADERS)
#     unapproved_url = "https://joinstatepolice.ny.gov/15-mile-run"

#     assert (
#         len([d for d in response.json["data"] if d["source_url"] == unapproved_url])
#         == 0
#     )


# def test_data_source_by_id_approved(client):
#     response = client.get("/data-sources-by-id/rec013MFNfBnrTpZj", headers=HEADERS)

#     assert response.json == "Data source not found."


# # search-tokens
# def test_search_tokens_data_sources(client):
#     response = client.get("/search-tokens?endpoint=data-sources")

#     assert len(response.json["data"]) > 0


# def test_search_tokens_data_source_by_id(client):
#     response = client.get("/search-tokens?endpoint=data-sources-by-id&arg1=reczwxaH31Wf9gRjS")

#     assert response.json["data_source_id"] == "reczwxaH31Wf9gRjS"


# def test_search_tokens_quick_search_complaints_allegheny_results(client):
#     response = client.get("/search-tokens?endpoint=quick-search&arg1=calls&arg2=chicago")

#     assert len(response.json["data"]) > 0


# # user
# def test_get_user(client):
#     response = client.get("/user", headers=HEADERS, json={"email": "test2", "password": "test"})

#     assert response


# def test_post_user(client):
#     headers = {"Authorization": f"Bearer {API_KEY}"}
#     response = client.post("/user", headers=HEADERS, json={"email": "test", "password": "test"})

#     with initialize_psycopg2_connection() as psycopg2_connection:
#         cursor = psycopg2_connection.cursor()
#         cursor.execute(f"DELETE FROM users WHERE email = 'test'")
#         psycopg2_connection.commit()

#     assert response.json["data"] == "Successfully added user"


# # archives
# def test_get_archives(client):
#     headers = {"Authorization": f"Bearer {API_KEY}"}
#     response = client.get("/archives", headers=HEADERS)

#     assert len(response.json[0]) > 0


# def test_get_archives_columns(client):
#     response = client.get("/archives", headers=HEADERS)

#     column_names = [
#         "id",
#         "source_url",
#         "update_frequency",
#         "last_cached",
#         "agency_name",
#     ]

#     assert not set(column_names).difference(response.json[0].keys())


# def test_put_archives(client):
#     current_datetime = datetime.datetime.now()
#     datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
#     response = client.put(
#         "/archives",
#         headers=HEADERS,
#         json=json.dumps(
#             {
#                 "id": "test",
#                 "last_cached": datetime_string,
#                 "broken_source_url_as_of": "",
#             }
#         ),
#     )

#     assert response.json["status"] == "success"


# def test_put_archives_brokenasof(client):
#     current_datetime = datetime.datetime.now()
#     datetime_string = current_datetime.strftime("%Y-%m-%d")
#     response = client.put(
#         "/archives",
#         headers=HEADERS,
#         json=json.dumps(
#             {
#                 "id": "test",
#                 "last_cached": datetime_string,
#                 "broken_source_url_as_of": datetime_string,
#             }
#         ),
#     )

#     assert response.json["status"] == "success"


# # agencies
# def test_agencies(client):
#     response = client.get("/agencies/1", headers=HEADERS)

#     assert len(response.json["data"]) > 0


# def test_agencies_pagination(client):
#     response1 = client.get("/agencies/1", headers=HEADERS)
#     response2 = client.get("/agencies/2", headers=HEADERS)

#     assert response1 != response2
