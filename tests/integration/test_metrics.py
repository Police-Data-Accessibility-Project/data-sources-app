from middleware.schema_and_dto_logic.primary_resource_dtos.metrics_dtos import (
    MetricsFollowedSearchesBreakdownRequestDTO,
)
from tests.helper_scripts.helper_classes.MultiAgencySetup import MultiAgencySetup
from tests.helper_scripts.helper_classes.MultiDataSourceSetup import (
    MultiDataSourceSetup,
)
from tests.helper_scripts.helper_classes.MultiFollowSetup import MultiFollowSetup
from tests.helper_scripts.helper_classes.MultiLocationSetup import MultiLocationSetup
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.conftest import test_data_creator_flask, monkeysession


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
    tdc.clear_test_data()

    data = tdc.request_validator.get_metrics_followed_searches_breakdown(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        dto=MetricsFollowedSearchesBreakdownRequestDTO(),
    )
    assert len(data["results"]) == 0

    mfs = MultiFollowSetup.setup(tdc)
    mas = MultiAgencySetup(tdc, mfs.mls)
    mds = MultiDataSourceSetup(tdc, mas)

    data = tdc.request_validator.get_metrics_followed_searches_breakdown(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        dto=MetricsFollowedSearchesBreakdownRequestDTO(),
    )
    assert len(data["results"]) == 3
