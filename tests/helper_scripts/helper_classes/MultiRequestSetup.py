from database_client.enums import RequestStatus
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
        self.request_pittsburgh = self.tdc.tdcdb.data_request()
        self.tdc.link_data_request_to_data_source(
            data_request_id=self.request_pittsburgh.id,
            data_source_id=mss.approved_source_pittsburgh.id,
        )
        self.tdc.tdcdb.link_data_request_to_location(
            self.request_pittsburgh.id, self.mls.pittsburgh_id
        )
        self.request_pennsylvania = self.tdc.tdcdb.data_request()
        self.tdc.link_data_request_to_data_source(
            data_request_id=self.request_pennsylvania.id,
            data_source_id=mss.approved_source_pennsylvania.id,
        )
        self.tdc.tdcdb.link_data_request_to_location(
            self.request_pennsylvania.id, self.mls.pennsylvania_id
        )
        self.request_federal = self.tdc.tdcdb.data_request()
        self.tdc.link_data_request_to_data_source(
            data_request_id=self.request_federal.id,
            data_source_id=mss.approved_source_federal.id,
        )
        self.tdc.tdcdb.link_data_request_to_location(
            self.request_federal.id, self.mls.orange_county_id
        )
        # Add completed requests as well
        self.completed_request_1 = self.tdc.tdcdb.data_request(
            request_status=RequestStatus.COMPLETE
        )
        self.tdc.link_data_request_to_data_source(
            data_request_id=self.completed_request_1.id,
            data_source_id=mss.approved_source_pittsburgh.id,
        )
        self.tdc.tdcdb.link_data_request_to_location(
            self.completed_request_1.id, self.mls.pittsburgh_id
        )
        self.completed_request_2 = self.tdc.tdcdb.data_request(
            request_status=RequestStatus.COMPLETE
        )
        self.tdc.link_data_request_to_data_source(
            data_request_id=self.completed_request_2.id,
            data_source_id=mss.approved_source_pennsylvania.id,
        )
        self.tdc.tdcdb.link_data_request_to_location(
            self.completed_request_2.id, self.mls.pennsylvania_id
        )
        self.completed_request_3 = self.tdc.tdcdb.data_request(
            request_status=RequestStatus.COMPLETE
        )
        self.tdc.link_data_request_to_data_source(
            data_request_id=self.completed_request_3.id,
            data_source_id=mss.approved_source_federal.id,
        )
        self.tdc.tdcdb.link_data_request_to_location(
            self.completed_request_3.id, self.mls.orange_county_id
        )
