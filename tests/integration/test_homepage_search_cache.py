# Below should not be enabled until https://github.com/Police-Data-Accessibility-Project/data-sources-app/issues/458
# def test_homepage_search_cache(flask_client_with_db, dev_db_client):
#     submitted_name = create_agency_entry_for_search_cache(dev_db_client)
#     tus = create_test_user_setup(
#         flask_client_with_db, permissions=[PermissionsEnum.DB_WRITE]
#     )
#
#     json_data = run_and_validate_request(
#         flask_client=flask_client_with_db,
#         http_method="get",
#         endpoint="/api/homepage-search-cache",
#         headers=tus.jwt_authorization_header,
#     )
#
#     airtable_uid = json_data["data"][0]["airtable_uid"]
#
#     run_and_validate_request(
#         flask_client=flask_client_with_db,
#         http_method="post",
#         endpoint=f"/api/homepage-search-cache",
#         headers=tus.jwt_authorization_header,
#         json={
#             "agency_airtable_uid": airtable_uid,
#             "search_results": ["found_results"],
#         },
#         expected_json_content={"message": "Search Cache Updated"},
#     )
#
#     new_json_data = run_and_validate_request(
#         flask_client=flask_client_with_db,
#         http_method="get",
#         endpoint="/api/homepage-search-cache",
#         headers=tus.jwt_authorization_header,
#     )
#
#     new_airtable_uid = new_json_data["data"][0]["airtable_uid"]
#     assert new_airtable_uid != airtable_uid
#
