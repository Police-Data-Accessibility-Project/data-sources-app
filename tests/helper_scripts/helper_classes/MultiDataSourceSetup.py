from db.enums import ApprovalStatus
from tests.helper_scripts.helper_classes.MultiAgencySetup import MultiAgencySetup
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


class MultiDataSourceSetup:

    def __init__(self, tdc: TestDataCreatorFlask, mas: MultiAgencySetup):
        self.tdc = tdc
        self.mas = mas
        self.approved_source_pittsburgh = self.tdc.data_source()
        self.tdc.link_data_source_to_agency(
            self.approved_source_pittsburgh.id, self.mas.pittsburgh_agency.id
        )
        self.approved_source_pennsylvania = self.tdc.data_source()
        self.tdc.link_data_source_to_agency(
            self.approved_source_pennsylvania.id, self.mas.pennsylvania_id.id
        )
        self.approved_source_federal = self.tdc.data_source()
        self.tdc.link_data_source_to_agency(
            self.approved_source_federal.id, self.mas.federal_agency.id
        )
        # Add pending data sources as well
        self.pending_source_1 = self.tdc.tdcdb.data_source(
            approval_status=ApprovalStatus.PENDING
        )
        self.tdc.link_data_source_to_agency(
            self.pending_source_1.id, self.mas.pittsburgh_agency.id
        )
        self.pending_source_2 = self.tdc.tdcdb.data_source(
            approval_status=ApprovalStatus.PENDING
        )
        self.tdc.link_data_source_to_agency(
            self.pending_source_2.id, self.mas.pennsylvania_id.id
        )
        self.pending_source_3 = self.tdc.tdcdb.data_source(
            approval_status=ApprovalStatus.PENDING
        )
        self.tdc.link_data_source_to_agency(
            self.pending_source_3.id, self.mas.federal_agency.id
        )
