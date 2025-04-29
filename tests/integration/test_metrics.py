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
    test_data_creator_flask: TestDataCreatorFlask,
):

    tdc = test_data_creator_flask

    data = tdc.request_validator.get_metrics_followed_searches_breakdown(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        dto=MetricsFollowedSearchesBreakdownRequestDTO(),
    )
    assert len(data["results"]) == 0

    mfs = MultiFollowSetup.setup(tdc)
    mas = MultiAgencySetup(tdc, mfs.mls)
    mds = MultiDataSourceSetup(tdc, mas)
    mrs = MultiRequestSetup(tdc, mfs.mls, mds)

    data = tdc.request_validator.get_metrics_followed_searches_breakdown(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        dto=MetricsFollowedSearchesBreakdownRequestDTO(),
    )
    assert len(data["results"]) == 3

    search_url_base = (
        f"{get_env_variable("VITE_VUE_APP_BASE_URL")}" f"/search/follow?location_id="
    )

    def validate_location(
        location_name: str,
        follower_count: int,
        source_count: int,
        request_count: int,
    ) -> None:
        for result in data["results"]:
            if result["location_name"] != location_name:
                continue
            assert result["follower_count"] == follower_count
            assert result["source_count"] == source_count
            assert result["request_count"] == request_count
            assert result["search_url"] == f"{search_url_base}{result['location_id']}"

    validate_location(
        location_name="Pennsylvania",
        follower_count=2,
        source_count=2,
        request_count=2,
    )
    validate_location(
        location_name="Pittsburgh, Allegheny, Pennsylvania",
        follower_count=3,
        source_count=1,
        request_count=1,
    )
    validate_location(
        location_name="Orange, California",
        follower_count=1,
        source_count=0,
        request_count=1,
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

    mfs = MultiFollowSetup.setup(tdc)

    data = tdc.request_validator.get_metrics_followed_searches_aggregate(
        headers=tdc.get_admin_tus().jwt_authorization_header,
    )
    assert data["total_followers"] == 3
    assert data["total_followed_searches"] == 6
    assert data["last_notification_date"] is None
