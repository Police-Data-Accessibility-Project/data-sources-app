from dataclasses import dataclass

from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup


@dataclass
class SearchTestSetup:
    tdc: TestDataCreatorFlask
    location_id: int
    tus: TestUserSetup
