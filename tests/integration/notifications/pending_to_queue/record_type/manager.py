from tests.helper_scripts.helper_classes.test_data_creator.db_client_.core import TestDataCreatorDBClient


class NotificationsPendingToQueueRecordTypeTestManager:

    def __init__(self, tdc: TestDataCreatorDBClient):
        self.tdc = tdc
        self.tdc.clear_test_data()
        self.db_client = tdc.db_client
        self.user_id_1 = self.tdc.user().id
        self.user_id_2 = self.tdc.user().id

        self.data_source_accident_id = self.tdc.data_source().id
        self.data_request_accident_id = self.tdc.data_request().id