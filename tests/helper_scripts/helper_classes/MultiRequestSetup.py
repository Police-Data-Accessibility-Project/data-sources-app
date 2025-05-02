from typing import Optional

from database_client.enums import RequestStatus
from tests.helper_scripts.helper_classes.MultiLocationSetup import MultiLocationSetup
from tests.helper_scripts.helper_classes.MultiDataSourceSetup import (
    MultiDataSourceSetup,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.test_dataclasses import TestDataRequestInfo


class MultiRequestSetup:

    def __init__(
        self,
        tdc: TestDataCreatorFlask,
        mls: MultiLocationSetup,
        mss: MultiDataSourceSetup,
    ):
        self.tdc = tdc
        self.mls = mls
        self.request_pittsburgh = self.setup_request(
            location_id=self.mls.pittsburgh_id,
            data_source_id=mss.approved_source_pittsburgh.id,
            request_status=RequestStatus.INTAKE,
        )
        self.request_pennsylvania = self.setup_request(
            location_id=self.mls.pennsylvania_id,
            data_source_id=mss.approved_source_pennsylvania.id,
            request_status=RequestStatus.INTAKE,
        )
        self.request_federal = self.setup_request(
            location_id=self.mls.orange_county_id,
            data_source_id=mss.approved_source_federal.id,
            request_status=RequestStatus.INTAKE,
        )
        # Add Ready to Start Requests
        self.request_ready_pittsburgh = self.setup_request(
            location_id=self.mls.pittsburgh_id,
            data_source_id=mss.approved_source_pittsburgh.id,
            request_status=RequestStatus.READY_TO_START,
        )
        self.request_ready_pennsylvania = self.setup_request(
            location_id=self.mls.pennsylvania_id,
            data_source_id=mss.approved_source_pennsylvania.id,
            request_status=RequestStatus.READY_TO_START,
        )
        self.request_ready_federal = self.setup_request(
            location_id=self.mls.orange_county_id,
            data_source_id=mss.approved_source_federal.id,
            request_status=RequestStatus.READY_TO_START,
        )
        # Add completed requests as well
        self.completed_request_pittsburgh = self.setup_request(
            location_id=self.mls.pittsburgh_id,
            data_source_id=mss.approved_source_pittsburgh.id,
            request_status=RequestStatus.COMPLETE,
        )
        self.completed_request_pennsylvania = self.setup_request(
            location_id=self.mls.pennsylvania_id,
            data_source_id=mss.approved_source_pennsylvania.id,
            request_status=RequestStatus.COMPLETE,
        )
        self.completed_request_federal = self.setup_request(
            location_id=self.mls.orange_county_id,
            data_source_id=mss.approved_source_federal.id,
            request_status=RequestStatus.COMPLETE,
        )

    def setup_request(
            self,
            data_source_id: int,
            location_id: Optional[int] = None,
            request_status: RequestStatus = RequestStatus.INTAKE,
    ) -> TestDataRequestInfo:
        request = self.tdc.tdcdb.data_request(
            request_status=request_status
        )
        self.tdc.link_data_request_to_data_source(
            data_request_id=request.id,
            data_source_id=data_source_id
        )
        self.tdc.tdcdb.link_data_request_to_location(
            data_request_id=request.id,
            location_id=location_id
        )
        return request