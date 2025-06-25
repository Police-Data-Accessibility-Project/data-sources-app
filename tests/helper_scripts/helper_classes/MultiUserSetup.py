from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


class MultiUserSetup:

    def __init__(
        self,
        tdc: TestDataCreatorFlask,
    ):
        self.tdc = tdc
        self.user_1 = tdc.standard_user()
        self.user_2 = tdc.standard_user()
        self.user_3 = tdc.standard_user()
