from db.client.core import DatabaseClient
from db.models.implementations.links.agency__location import LinkAgencyLocation
from db.models.implementations.core.agency.core import Agency
from endpoints.v3.source_manager.sync.agencies.shared.content import (
    AgencySyncContentModel,
)
from endpoints.v3.source_manager.sync.agencies.update.request import (
    UpdateAgenciesOuterRequest,
    UpdateAgenciesInnerRequest,
)
from middleware.enums import JurisdictionType, AgencyType
from tests.integration.v3.helpers.api_test_helper import APITestHelper


def test_source_manager_agencies_update_happy_path(
    agency_id_1: int,
    agency_id_2: int,
    pittsburgh_id: int,
    allegheny_id: int,
    live_database_client: DatabaseClient,
    api_test_helper: APITestHelper,
):
    api_test_helper.request_validator.post_v3(
        url="/source-manager/agencies/update",
        json=UpdateAgenciesOuterRequest(
            agencies=[
                UpdateAgenciesInnerRequest(
                    app_id=agency_id_1,
                    content=AgencySyncContentModel(
                        name="Modified Name 1",
                        jurisdiction_type=JurisdictionType.PORT,
                        agency_type=AgencyType.AGGREGATED,
                        no_web_presence=True,
                        defunct_year=2023,
                        location_ids=[allegheny_id],
                    ),
                ),
                UpdateAgenciesInnerRequest(
                    app_id=agency_id_2,
                    content=AgencySyncContentModel(
                        name="Modified Name 2",
                        defunct_year=None,
                        location_ids=[pittsburgh_id],
                        jurisdiction_type=JurisdictionType.STATE,
                        agency_type=AgencyType.POLICE,
                        no_web_presence=False,
                    ),
                ),
            ]
        ).model_dump(mode="json", exclude_unset=True),
    )

    agencies: list[dict] = live_database_client.get_all(Agency)
    assert len(agencies) == 2

    agency_1: dict = agencies[0]
    assert agency_1["id"] == agency_id_1
    assert agency_1["name"] == "Modified Name 1"
    assert agency_1["jurisdiction_type"] == JurisdictionType.PORT.value
    assert agency_1["agency_type"] == AgencyType.AGGREGATED.value
    assert agency_1["no_web_presence"] is True
    assert agency_1["defunct_year"] == "2023"

    agency_2: dict = agencies[1]
    assert agency_2["id"] == agency_id_2
    assert agency_2["name"] == "Modified Name 2"
    assert agency_2["jurisdiction_type"] == JurisdictionType.STATE.value
    assert agency_2["agency_type"] == AgencyType.POLICE.value
    assert agency_2["no_web_presence"] is False
    assert agency_2["defunct_year"] is None

    links: list[dict] = live_database_client.get_all(LinkAgencyLocation)
    assert len(links) == 2
    link_tuples: set[tuple[int, int]] = {
        (link["agency_id"], link["location_id"]) for link in links
    }
    assert link_tuples == {
        (agency_1["id"], allegheny_id),
        (agency_2["id"], pittsburgh_id),
    }
