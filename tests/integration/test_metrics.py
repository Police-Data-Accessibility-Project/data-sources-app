import datetime

from database_client.enums import SortOrder
from middleware.schema_and_dto_logic.primary_resource_dtos.metrics_dtos import (
    MetricsFollowedSearchesBreakdownRequestDTO,
)
from middleware.util import get_env_variable
from tests.helper_scripts.helper_classes.MultiAgencySetup import MultiAgencySetup
from tests.helper_scripts.helper_classes.MultiDataSourceSetup import (
    MultiDataSourceSetup,
)
from tests.helper_scripts.helper_classes.MultiFollowSetup import MultiFollowSetup
from tests.helper_scripts.helper_classes.MultiRequestSetup import MultiRequestSetup
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.conftest import test_data_creator_flask


def test_metrics(test_data_creator_flask: TestDataCreatorFlask):

    tdc = test_data_creator_flask
    tdc.link_data_source_to_agency(tdc.data_source().id, tdc.agency().id)
    metrics = tdc.request_validator.get_metrics(
        headers=tdc.get_admin_tus().jwt_authorization_header
    )

    assert metrics["source_count"] > 0
    assert metrics["agency_count"] > 0
    assert metrics["county_count"] > 0
    assert metrics["state_count"] > 0


def test_metrics_followed_searches_breakdown(
    test_data_creator_flask: TestDataCreatorFlask, monkeypatch
):
    monkeypatch.setenv("VITE_VUE_APP_BASE_URL", "https://example.com")

    tdc = test_data_creator_flask
    last_notification_datetime = tdc.tdcdb.notification_log()

    data = tdc.request_validator.get_metrics_followed_searches_breakdown(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        dto=MetricsFollowedSearchesBreakdownRequestDTO(),
    )
    assert len(data["results"]) == 0

    mfs = MultiFollowSetup.setup(tdc)
    mas = MultiAgencySetup(tdc, mfs.mls)
    mds = MultiDataSourceSetup(tdc, mas)
    mrs = MultiRequestSetup(tdc, mfs.mls, mds)

    # Set some results to be pre-notification
    pre_notification_datetime = last_notification_datetime - datetime.timedelta(days=1)
    # Data Source Pittsburgh
    tdc.db_client.update_data_source(
        entry_id=int(mds.approved_source_pittsburgh.id),
        column_edit_mappings={"created_at": pre_notification_datetime},
    )
    # Ready Requests Pittsburgh and Pennsylvania
    for request in [mrs.request_ready_pittsburgh, mrs.request_ready_pennsylvania]:
        tdc.db_client.update_data_request(
            entry_id=int(request.id),
            column_edit_mappings={
                "date_status_last_changed": pre_notification_datetime
            },
        )
    # Orange County User Follower
    tdc.db_client._update_entry_in_table(
        table_name="link_user_followed_location",
        id_column_name="user_id",
        entry_id=int(mfs.mus.user_3.user_info.user_id),
        column_edit_mappings={"created_at": pre_notification_datetime},
    )

    data = tdc.request_validator.get_metrics_followed_searches_breakdown(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        dto=MetricsFollowedSearchesBreakdownRequestDTO(),
    )
    assert len(data["results"]) == 3

    search_url_base = (
        f"{get_env_variable("VITE_VUE_APP_BASE_URL")}" f"/search/results?location_id="
    )

    def validate_location(
        location_name: str,
        follower_count: int,
        follower_change: int,
        source_count: int,
        source_change: int,
        complete_request_count: int,
        complete_request_change: int,
        approved_request_count: int,
        approved_request_change: int,
    ) -> None:
        pairs = [
            ("follower_count", follower_count),
            ("follower_change", follower_change),
            ("source_count", source_count),
            ("source_change", source_change),
            ("completed_requests_count", complete_request_count),
            ("completed_requests_change", complete_request_change),
            ("approved_requests_count", approved_request_count),
            ("approved_requests_change", approved_request_change),
        ]

        for result in data["results"]:
            if result["location_name"] != location_name:
                continue
            try:
                for key, value in pairs:
                    assert result[key] == value
                assert (
                    result["search_url"] == f"{search_url_base}{result['location_id']}"
                )
            except AssertionError as e:
                raise AssertionError(
                    f"Assertion error in {result['location_name']}: {e}"
                )

    validate_location(
        location_name="Pennsylvania",
        follower_count=2,
        follower_change=2,
        source_count=2,
        source_change=1,
        complete_request_count=2,
        complete_request_change=2,
        approved_request_count=2,
        approved_request_change=0,
    )
    validate_location(
        location_name="Pittsburgh, Allegheny, Pennsylvania",
        follower_count=3,
        follower_change=2,
        source_count=1,
        source_change=0,
        complete_request_count=1,
        complete_request_change=1,
        approved_request_count=1,
        approved_request_change=0,
    )
    validate_location(
        location_name="Orange, California",
        follower_count=1,
        follower_change=0,
        source_count=0,
        source_change=0,
        complete_request_count=1,
        complete_request_change=1,
        approved_request_count=1,
        approved_request_change=1,
    )

    # Test pagination
    data = tdc.request_validator.get_metrics_followed_searches_breakdown(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        dto=MetricsFollowedSearchesBreakdownRequestDTO(page=2),
    )
    assert len(data["results"]) == 0

    # Test sorting
    data = tdc.request_validator.get_metrics_followed_searches_breakdown(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        dto=MetricsFollowedSearchesBreakdownRequestDTO(sort_by="follower_count"),
    )
    results = data["results"]
    assert len(results) == 3

    assert results[0]["location_name"] == "Pittsburgh, Allegheny, Pennsylvania"
    assert results[1]["location_name"] == "Pennsylvania"
    assert results[2]["location_name"] == "Orange, California"

    data = tdc.request_validator.get_metrics_followed_searches_breakdown(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        dto=MetricsFollowedSearchesBreakdownRequestDTO(
            sort_by="follower_count", sort_order=SortOrder.ASCENDING
        ),
    )
    results = data["results"]
    assert len(results) == 3

    assert results[0]["location_name"] == "Orange, California"
    assert results[1]["location_name"] == "Pennsylvania"
    assert results[2]["location_name"] == "Pittsburgh, Allegheny, Pennsylvania"

    data = tdc.request_validator.get_metrics_followed_searches_breakdown(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        dto=MetricsFollowedSearchesBreakdownRequestDTO(
            sort_by="location_name", sort_order=SortOrder.ASCENDING
        ),
    )
    results = data["results"]
    assert len(results) == 3

    assert results[0]["location_name"] == "Orange, California"
    assert results[1]["location_name"] == "Pennsylvania"
    assert results[2]["location_name"] == "Pittsburgh, Allegheny, Pennsylvania"


def test_metrics_followed_searches_aggregate(test_data_creator_flask):
    tdc = test_data_creator_flask
    tdc.clear_test_data()
    last_notification_datetime = tdc.tdcdb.notification_log()

    mfs = MultiFollowSetup.setup(tdc)

    data = tdc.request_validator.get_metrics_followed_searches_aggregate(
        headers=tdc.get_admin_tus().jwt_authorization_header,
    )
    assert data["total_followers"] == 3
    assert data["total_followed_searches"] == 6
    assert data["last_notification_date"] == last_notification_datetime.strftime(
        "%Y-%m-%d"
    )
