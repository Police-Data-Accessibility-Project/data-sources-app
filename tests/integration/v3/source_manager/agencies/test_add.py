from db.models.implementations.links.agency__location import LinkAgencyLocation
from db.models.implementations.core.agency.core import Agency
from endpoints.v3.source_manager.sync.agencies.add.request import (
    AddAgenciesOuterRequest,
    AddAgenciesInnerRequest,
)
from endpoints.v3.source_manager.sync.agencies.shared.content import AgencySyncContentModel
from endpoints.v3.source_manager.sync.shared.models.response.add import (
    SourceManagerSyncAddOuterResponse,
)

from middleware.enums import JurisdictionType, AgencyType
from tests.integration.v3.helpers.api_test_helper import APITestHelper


def test_source_manager_agencies_add(
    api_test_helper: APITestHelper,
    pennsylvania_id: int,
    allegheny_id: int,
    pittsburgh_id: int,
):
    response: SourceManagerSyncAddOuterResponse = (
        api_test_helper.request_validator.post_v3(
            url="/source-manager/agencies/add",
            json=AddAgenciesOuterRequest(
                agencies=[
                    AddAgenciesInnerRequest(
                        request_id=1,
                        content=AgencySyncContentModel(
                            name="test",
                            jurisdiction_type=JurisdictionType.STATE,
                            agency_type=AgencyType.POLICE,
                            no_web_presence=False,
                            defunct_year=None,
                            location_ids=[pennsylvania_id, pittsburgh_id],
                        )
                    ),
                    AddAgenciesInnerRequest(
                        request_id=2,
                        content=AgencySyncContentModel(
                            name="test2",
                            jurisdiction_type=JurisdictionType.COUNTY,
                            agency_type=AgencyType.POLICE,
                            no_web_presence=False,
                            defunct_year=2022,
                            location_ids=[allegheny_id],
                        )
                    ),
                ]
            ).model_dump(mode="json"),
            expected_model=SourceManagerSyncAddOuterResponse,
        )
    )

    # Check for existence of two agencies
    agencies: list[dict] = api_test_helper.db_client.get_all(Agency)
    assert len(agencies) == 2
    # Check Agency 1
    agency_1: dict = agencies[0]
    assert agency_1["id"] == response.entities[0].app_id
    assert agency_1["name"] == "test"
    assert agency_1["jurisdiction_type"] == JurisdictionType.STATE.value
    assert agency_1["agency_type"] == AgencyType.POLICE.value
    assert agency_1["no_web_presence"] is False
    assert agency_1["defunct_year"] is None

    # Check Agency 2
    agency_2: dict = agencies[1]
    assert agency_2["id"] == response.entities[1].app_id
    assert agency_2["name"] == "test2"
    assert agency_2["jurisdiction_type"] == JurisdictionType.COUNTY.value
    assert agency_2["agency_type"] == AgencyType.POLICE.value
    assert agency_2["no_web_presence"] is False
    assert agency_2["defunct_year"] == "2022"

    # Check for existence of three links
    links: list[dict] = api_test_helper.db_client.get_all(LinkAgencyLocation)
    assert len(links) == 3
    link_tuples: set[tuple[int, int]] = {
        (link["agency_id"], link["location_id"]) for link in links
    }
    assert link_tuples == {
        (agency_1["id"], pennsylvania_id),
        (agency_1["id"], pittsburgh_id),
        (agency_2["id"], allegheny_id),
    }
