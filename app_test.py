import pytest
from app import app
from flask_restful import Api
from middleware.quick_search_query import unaltered_search_query, quick_search_query, QUICK_SEARCH_TEST_SQL, INSERT_LOG_QUERY
from middleware.data_source_queries import data_source_by_id_query, data_source_by_id_results, APPROVED_COLUMNS
import datetime
import json
import sqlite3

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
            "url_status": "ok",
            "approval_status": "approved",
        },
        {
            "airtable_uid": "recUGIoPQbJ6laBmr",
            "name": "311 Calls for City of Chicago",
            "description": "311 Service Requests received by the City of Chicago. This dataset includes requests created after the launch of the new 311 system on 12/18/2018 and some records from the previous system, indicated in the LEGACY\\_RECORD column.\n\nIncluded as a Data Source because in some cities 311 calls lead to police response; that does not appear to be the case in Chicago.\n",
            "record_type": "Calls for Service",
            "source_url": "https://data.cityofchicago.org/Service-Requests/311-Service-Requests/v6vf-nfxy",
            "record_format": '["CSV", "XML", "RDF", "RSS"]',
            "coverage_start": "2018-12-18",
            "coverage_end": None,
            "agency_supplied": "False",
            "agency_name": "Chicago Police Department - IL",
            "municipality": "Chicago",
            "state_iso": "IL",
            "url_status": "ok",
            "approval_status": "approved",
        },
        {
            "airtable_uid": "rec8zJuEOvhAZCfAD",
            "name": "Pittsburgh Police Complaints and Disciplinary Actions 2013-2022",
            "description": 'This news article contains several data tables. Most useful are the two near the bottom. "Pittsburgh Police Disciplinary Action Report data 2013-2022" and "Pittsburgh Office of Municipal Investigations police-related complaint data 2013-2022". Both are in paginated HTML tables and can be downloaded as a CSV by clicking a "Get the data" link.\n',
            "record_type": "Complaints & Misconduct",
            "source_url": "https://www.publicsource.org/pittsburgh-bureau-police-discipline-complaints-disciplinary-matrix-new-chief/",
            "record_format": '["CSV", "HTML table"]',
            "coverage_start": "2013-01-01",
            "coverage_end": "2022-12-31",
            "agency_supplied": "False",
            "agency_name": "Pittsburgh Bureau of Police - PA",
            "municipality": "Pittsburgh",
            "state_iso": "PA",
            "url_status": "ok",
            "approval_status": "approved",
        },
        {
            "airtable_uid": "rec8gO2K86yk9mQIU",
            "name": "Officer Involved Shootings for Philadelphia Police Department - PA",
            "description": None,
            "record_type": "Officer Involved Shootings",
            "source_url": "https://www.phillypolice.com/ois/",
            "record_format": None,
            "coverage_start": "2015-01-01",
            "coverage_end": None,
            "agency_supplied": True,
            "agency_name": "Philadelphia Police Department - PA",
            "municipality": "Philadelphia",
            "state_iso": "PA",
        },
    ]
    all_columns = APPROVED_COLUMNS + ["airtable_uid"]
    for row in data_source_rows:
        valid_row = {k: v for k, v in row.items() if k in all_columns}
        clean_row = [r if r is not None else "" for r in valid_row.values()]
        fully_clean_row = [r if r is not True else "True" for r in clean_row]
        fully_clean_row_str = "'" + "', '".join(fully_clean_row) + "'"
        col_str = ", ".join(valid_row.keys())
        db_session.execute(
            f"insert into data_sources ({col_str}) values ({fully_clean_row_str})"
        )

    db_session.execute(
        "insert into agency_source_link (link_id, airtable_uid, agency_described_linked_uid) values (1, 'rec00T2YLS2jU7Tbn', 'recv9fMNEQTbVarj2')"
    )
    db_session.execute(
        "insert into agency_source_link (link_id, airtable_uid, agency_described_linked_uid) values (2, 'rec8zJuEOvhAZCfAD', 'recxUlLdt3Wwov6P1')"
    )
    db_session.execute(
        "insert into agency_source_link (link_id, airtable_uid, agency_described_linked_uid) values (3, 'recUGIoPQbJ6laBmr', 'recv9fMNEQTbVarj2')"
    )
    db_session.execute(
        "insert into agency_source_link (link_id, airtable_uid, agency_described_linked_uid) values (4, 'rec8gO2K86yk9mQIU', 'recRvBpZqXM8mjddz')"
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
        ),
        (
            "Pittsburgh Bureau of Police - PA",
            "Pittsburgh Bureau of Police",
            "http://pittsburghpa.gov/police/",
            "local",
            "PA",
            "Pittsburgh",
            "42003",
            '["Allegheny"]',
            40.450523,
            -80.02128,
            None,
            "recxUlLdt3Wwov6P1",
            46,
            "law enforcement/police",
            None,
            "15233",
            '["recJK8P5rWlLjSzgc", "recCkota2A2S7Z33q", "recAD4tPHp4IndO2c", "recIwxfj2Ko77ySMD", "recF3bBivp59xdVBW", "recwj8eU8vdTNSEEu", "rec4G2iyEb1UiYfh2", "recJOzE2fe0Srdn4X", "recOlNMNivWF9sumN", "recEFwKevbY7P5DPS", "recvfbfIwGJeKH1OB", "recCvmgUInsKZpP3k", "recrm2fG7gztK7Tfg", "recwHAhLNsz52XvqX", "recX0ez0i7fcDQDx1", "recuvx89h9QZpRSZV", "recEFNJB8aOIF7ucx", "rec8ILhFGC9694CMS", "rec3Oc64eiYe0Cphx", "recLsGQ6yBEvJXTc3", "recRIejFKCgQgsX3l", "recd4qlLMmoLb4Rds", "recmhO1J5gh9pzgUP", "recJ46NmxuyjkoonW", "recmMakoz1eKO6rdC", "recAGF2VxFsOSZHqb", "recBSLCZXuVj1Zy0R", "recV3HCVPrqP31sqp", "rec1LIccYrPQVAdgL", "recgyEBNyh7VNyrAH", "recBjOdBK3XuSCTZy", "recUIXIJKuWleztqy", "recw9GbEslgN5w6zt", "recSQKpHfaj15B249", "recjeyUxVgQh2gqUj", "recbv6UOuUesjrXgI", "rec5E9yiFbuY3dWEc", "recFcv4IvAkcrlTdF", "recP5qX2qNlsuv7Np", "reckDUGoOgKx3yjqf", "rectnkXtlHLV26ZQP", "recrVIpgDHsFbB8Jn", "receW1cbs1sDMQvRl", "recQY7IEhVIIFL7wv", "recsIealZCldEKOlX", "rec7OiCCI6XxDy6ti", "rec2doMHsYVl5i6Y7", "rec8zJuEOvhAZCfAD", "recORxPfDzvYoBO4E", "recwDqMgD47XqrkbK", "rec40yyKK0f5lua4Z"]',
            None,
            datetime.datetime(2023, 3, 23, 18, 0, 3, tzinfo=datetime.timezone.utc),
            datetime.date(2023, 11, 3),
            True,
            None,
            '{"id": "usrtLIB4Vr3jTH8Ro", "email": "josh.chamberlain@pdap.io", "name": "Josh Chamberlain"}',
            None,
            datetime.datetime(2022, 8, 18, 18, 49, 27, tzinfo=datetime.timezone.utc),
            "recACF0SHugE9icVH",
        ),
        (
            "Philadelphia Police Department - PA",
            "Philadelphia Police Department",
            "https://www.phillypolice.com/districts/22nd/index.html",
            "local",
            "PA",
            "Philadelphia",
            "42101",
            '["Philadelphia"]',
            39.980556,
            -75.16209,
            None,
            "recRvBpZqXM8mjddz",
            17,
            "law enforcement/police",
            None,
            "19121",
            '["recXlFbG4J6pkBdKn", "recHd6j7LT6iMWWzf", "rec7IloZhaAsjpGwt", "recnKS6MwvODb4okj", "recgsrvT60fwJK2zv", "rec8gO2K86yk9mQIU", "recsvkVLs3NHh6fEk", "recIWjgyMq9umFWdv", "recIZvrJ1JJQddfGP", "recVcjF6jZJ7bkujw", "rec8r19ChbuSwpSpJ", "recPSQHatnNFV7H29", "recNH6V5a4TpINhMj", "recwbcrNqdutfgrE7", "rec5RlBXnQOEpGJQz", "recAbsBlvWEsCifvz", "recanjxF6Ph3SNA5P", "recX4kQbeRFch59DU", "recpqSEq8bYcNvIv9", "recVyLpoO48utQuq6"]',
            None,
            datetime.datetime(2023, 5, 16, 17, 37, 6, tzinfo=datetime.timezone.utc),
            datetime.date(2023, 5, 2),
            True,
            None,
            '{"id": "usrtLIB4Vr3jTH8Ro", "email": "josh.chamberlain@pdap.io", "name": "Josh Chamberlain"}',
            None,
            datetime.datetime(2022, 8, 18, 18, 50, 49, tzinfo=datetime.timezone.utc),
            "rec6tZ0VTIMmKXCkH",
        ),
    ]
    clean_row = [r if r is not None else "" for r in agencies_rows[0]]
    fully_clean_row = [str(r) for r in clean_row]
    fully_clean_row_str = "'" + "', '".join(fully_clean_row) + "'"

    db_session.execute(f"insert into agencies values ({fully_clean_row_str})")
    db_session.execute(f"insert into state_names values (1, 'IL', 'Illinois')")
    db_session.execute(f"insert into state_names values (2, 'PA', 'Pennsylvania')")

    # sql_query_log = f"INSERT INTO quick_search_query_logs (id, search, location, results, result_count, datetime_of_request, created_at) VALUES (1, 'test', 'test', '', 0, '{DATETIME_STRING}', '{DATETIME_STRING}')"
    # db_session.execute(sql_query_log)

    yield db_session
    connection.close()


# @pytest.fixture
# def setup_db(session):


# unit tests
def test_quick_search_queries(session):
    session.execute(QUICK_SEARCH_TEST_SQL.format("calls", "chicago"))
    results = session.fetchall()

    assert len(results) > 0

    results_str = json.dumps(results)
    print(INSERT_LOG_QUERY.format("calls", "chicago", results_str, 2, DATETIME_STRING))
    session.execute(
        INSERT_LOG_QUERY.format("calls", "chicago", results_str, 2, DATETIME_STRING)
    )
    session.execute(
        f"SELECT * FROM quick_search_query_logs WHERE datetime_of_request = '{DATETIME_STRING}'"
    )
    logs = session.fetchall()

    assert len(logs) > 0


# quick-search
def test_quicksearch_columns():
    query_results = [('rec00T2YLS2jU7Tbn', 'Calls for Service for Chicago Police Department - IL', None, 'Calls for Service', 'https://informationportal.igchicago.org/911-calls-for-cpd-service/', None, datetime.date(2019, 1, 1), None, True, 'Chicago Police Department - IL', 'Chicago', 'IL'), ('recUGIoPQbJ6laBmr', '311 Calls for City of Chicago', '311 Service Requests received by the City of Chicago. This dataset includes requests created after the launch of the new 311 system on 12/18/2018 and some records from the previous system, indicated in the LEGACY\\_RECORD column.\n\nIncluded as a Data Source because in some cities 311 calls lead to police response; that does not appear to be the case in Chicago.\n', 'Calls for Service', 'https://data.cityofchicago.org/Service-Requests/311-Service-Requests/v6vf-nfxy', '["CSV", "XML", "RDF", "RSS"]', datetime.date(2018, 12, 18), None, False, 'Chicago Police Department - IL', 'Chicago', 'IL')]
    response = quick_search_query(search="", location="", test_query_results=query_results)
    column_names = [
        "airtable_uid",
        "data_source_name",
        "record_type",
        "source_url",
        "record_format",
        "coverage_start",
        "coverage_end",
        "agency_name",
        "municipality",
        "state_iso",
    ]
    print(response["data"])

    assert not set(column_names).difference(response["data"][0].keys())
    assert type(response["data"][1]["record_format"]) == list


# data-sources
def test_data_source_by_id_columns(client):
    query_results = ('Calls for Service for Asheville Police Department - NC', None, None, 'Calls for Service', 'https://services.arcgis.com/aJ16ENn1AaqdFlqx/arcgis/rest/services/APD_CAD_911_Calls_2006/FeatureServer/0', True, None, None, None, None, datetime.date(2006, 1, 1), datetime.date(2006, 12, 31), None, None, None, None, None, '["API", "Download"]', 'ArcGIS', '["GIS / Shapefile"]', None, None, None, 'https://docs.google.com/document/d/143a0LoGwNwmmHxJu1msxjOFAfAXPk7otQSWkrLtUDk0/edit?usp=sharing', 'https://pypi.org/project/openpolicedata/', datetime.datetime(2023, 3, 2, 18, 36, 27, tzinfo=datetime.timezone.utc), datetime.datetime(2023, 11, 8, 19, 6, 38, tzinfo=datetime.timezone.utc), 'ok', None, '{"id": "usrtLIB4Vr3jTH8Ro", "email": "josh.chamberlain@pdap.io", "name": "Josh Chamberlain"}', None, None, 'approved', None, None, None, None, None, None, None, 'https://www.ashevillenc.gov/department/police', 18, 'law enforcement/police', None, 'Asheville Police Department', 'local', 'NC', 'Asheville', '28801', '37021', '["Buncombe"]', 35.594677, -82.54986, '["recpWxJ9JVa6BtLi5", "reczwxaH31Wf9gRjS", "recBd7NrWsvfTyDk0", "recy24QB6I8FCVrQr", "recW6aQGuNyzedIDl", "recmrXPvQn9Gtfpba", "recsojoTxJ3g08qKl", "recTUW1QUZpsGVxoJ", "reckqhpMEvDgiDGXF", "recjnLeosesVTaW2r", "reccrwbvTL6Ttd8XT", "reckiy2nuY5iRptBm", "recyJMD6eYF9Ln98B", "recLdzmQMXC3XuPWU", "recRNvjKBo5LkUBS9", "recKFoiPMOmWFZvqM", "recordd7DcM3raQF7", "recV35fyFlof4pQXP"]', None, datetime.datetime(2023, 5, 16, 17, 37, 6, tzinfo=datetime.timezone.utc), datetime.date(2023, 3, 2), True, None, '{"id": "usrtLIB4Vr3jTH8Ro", "email": "josh.chamberlain@pdap.io", "name": "Josh Chamberlain"}', datetime.datetime(2022, 8, 18, 18, 50, 38, tzinfo=datetime.timezone.utc), 'recrCy8hHYuxC8ZhU', None, 'reczwxaH31Wf9gRjS', 'recJDGmbd7UMFcfa0', 'Asheville Police Department - NC')
    response = data_source_by_id_query("", query_results, {})
    column_names = [
        "description",
        "record_type",
        "agency_name",
        "state_iso",
        "county_name",
        "municipality",
        "agency_type",
        "jurisdiction_type",
        "source_url",
        "readme_url",
        "access_type",
        "record_format",
        "detail_level",
        "size",
        "access_type",
        "access_notes",
        "records_not_online",
        "agency_supplied",
        "supplying_entity",
        "agency_originated",
        "originating_entity",
        "coverage_start",
        "coverage_end",
        "source_last_updated",
        "update_frequency",
        "update_method",
        "retention_schedule",
        "number_of_records_available",
        "scraper_url",
        "data_source_created",
        "data_source_id",
        "agency_id",
    ]

    assert not set(column_names).difference(response.keys())


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


# search-tokens


# user



# def test_post_user(client):
#     response = client.post(
#         "/user", headers=HEADERS, json={"email": "test", "password": "test"}
#     )

#     # with initialize_psycopg2_connection() as psycopg2_connection:
#     #     cursor = psycopg2_connection.cursor()
#     #     cursor.execute(f"DELETE FROM users WHERE email = 'test'")
#     #     psycopg2_connection.commit()

#     assert response.json["data"] == "Successfully added user"


# archives
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



# agencies

