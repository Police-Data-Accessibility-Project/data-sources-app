from middleware.enums import JurisdictionType
from tests.helper_scripts.helper_classes.MultiLocationSetup import MultiLocationSetup
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)


class MultiAgencySetup:
    def __init__(self, tdc: TestDataCreatorFlask, mls: MultiLocationSetup):
        self.tdc = tdc
        self.mls = mls
        self.pittsburgh_agency = self.tdc.agency(
            location_ids=[self.mls.pittsburgh_id], agency_name="Pittsburgh Agency"
        )
        self.pennsylvania_id = self.tdc.agency(
            location_ids=[self.mls.pennsylvania_id],
            agency_name="Multi-State Agency",
            jurisdiction_type=JurisdictionType.STATE,
        )
        self.federal_agency = self.tdc.agency(
            agency_name="Federal Agency", jurisdiction_type=JurisdictionType.FEDERAL
        )
