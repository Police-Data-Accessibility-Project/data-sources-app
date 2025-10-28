from dataclasses import dataclass

from db.client.core import DatabaseClient
from tests.helpers.helper_classes.test_data_creator.db_client_.core import (
    TestDataCreatorDBClient,
)
from tests.integration.v3.helpers.request_validator import RequestValidatorFastAPI


@dataclass
class APITestHelper:
    request_validator: RequestValidatorFastAPI
    db_data_creator: TestDataCreatorDBClient

    @property
    def db_client(self) -> DatabaseClient:
        return self.db_data_creator.db_client
