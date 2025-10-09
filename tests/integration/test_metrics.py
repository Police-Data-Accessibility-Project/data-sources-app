import datetime

from db.enums import SortOrder
from middleware.constants import DATE_FORMAT
from middleware.schema_and_dto.dtos.metrics import (
    MetricsFollowedSearchesBreakdownRequestDTO,
)
from middleware.util.env import get_env_variable
from tests.helpers.helper_classes.MultiAgencySetup import MultiAgencySetup
from tests.helpers.helper_classes.MultiDataSourceSetup import (
    MultiDataSourceSetup,
)
from tests.helpers.helper_classes.MultiFollowSetup import MultiFollowSetup
from tests.helpers.helper_classes.MultiRequestSetup import MultiRequestSetup
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


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
        f"{get_env_variable('VITE_VUE_APP_BASE_URL')}/search/results?location_id="
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

    MultiFollowSetup.setup(tdc)

    data = tdc.request_validator.get_metrics_followed_searches_aggregate(
        headers=tdc.get_admin_tus().jwt_authorization_header,
    )
    assert data["total_followers"] == 3
    assert data["total_followed_searches"] == 6
    assert data["last_notification_date"] == last_notification_datetime.strftime(
        DATE_FORMAT
    )
