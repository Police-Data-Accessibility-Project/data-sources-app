from tests.helper_scripts.helper_classes.MultiLocationSetup import MultiLocationSetup
from tests.helper_scripts.helper_classes.MultiUserSetup import MultiUserSetup
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)


class MultiFollowSetup:
    def __init__(
        self, tdc: TestDataCreatorFlask, mls: MultiLocationSetup, mus: MultiUserSetup
    ):
        self.tdc = tdc
        self.mls = mls
        self.mus = mus
        # All three users follow Pittsburgh
        for user in [self.mus.user_1, self.mus.user_2, self.mus.user_3]:
            self.tdc.tdcdb.user_follow_location(
                user_id=user.user_info.user_id,
                location_id=self.mls.pittsburgh_id,
            )
        # User 1 and 2 follow Pennsylvania
        for user in [self.mus.user_1, self.mus.user_2]:
            self.tdc.tdcdb.user_follow_location(
                user_id=user.user_info.user_id,
                location_id=self.mls.pennsylvania_id,
            )
        # User 3 follows Orange County
        self.follow_3 = self.tdc.tdcdb.user_follow_location(
            user_id=self.mus.user_3.user_info.user_id,
            location_id=self.mls.orange_county_id,
        )

    @staticmethod
    def setup(tdc: TestDataCreatorFlask) -> "MultiFollowSetup":
        mls = MultiLocationSetup(tdc.tdcdb)
        mus = MultiUserSetup(tdc)
        return MultiFollowSetup(tdc, mls, mus)
