from tests.helper_scripts.helper_classes.MultiLocationSetup import MultiLocationSetup
from tests.helper_scripts.helper_classes.MultiDataSourceSetup import (
    MultiDataSourceSetup,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)


class MultiRequestSetup:

    def __init__(
        self,
        tdc: TestDataCreatorFlask,
        mls: MultiLocationSetup,
        mss: MultiDataSourceSetup,
    ):
        self.tdc = tdc
        self.mls = mls
        self.request_1 = self.tdc.tdcdb.data_request()
        self.tdc.link_data_request_to_data_source(self.request_1.id, mss.source_1.id)
        self.request_2 = self.tdc.tdcdb.data_request()
        self.tdc.link_data_request_to_data_source(self.request_2.id, mss.source_2.id)
        self.request_3 = self.tdc.tdcdb.data_request()
        self.tdc.link_data_request_to_data_source(self.request_3.id, mss.source_3.id)
