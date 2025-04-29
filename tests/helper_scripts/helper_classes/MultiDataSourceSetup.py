from tests.helper_scripts.helper_classes.MultiAgencySetup import MultiAgencySetup
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)


class MultiDataSourceSetup:

    def __init__(self, tdc: TestDataCreatorFlask, mas: MultiAgencySetup):
        self.tdc = tdc
        self.mas = mas
        self.source_1 = self.tdc.data_source()
        self.tdc.link_data_source_to_agency(
            self.source_1.id, self.mas.pittsburgh_agency.id
        )
        self.source_2 = self.tdc.data_source()
        self.tdc.link_data_source_to_agency(
            self.source_2.id, self.mas.pennsylvania_id.id
        )
        self.source_3 = self.tdc.data_source()
        self.tdc.link_data_source_to_agency(
            self.source_3.id, self.mas.federal_agency.id
        )
