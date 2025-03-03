from dataclasses import dataclass
from typing import Optional

from tests.helper_scripts.run_and_validate_request import run_and_validate_request


@dataclass
class EndpointCallInfo:
    expected_json_content: Optional[dict] = None
    authorization_header: Optional[dict] = None
    query_parameters: Optional[dict] = None


class EndpointCaller:
    """
    Provides a simplified interface for calling endpoints
    """

    def __init__(self, flask_client):
        self.flask_client = flask_client

    def notifications_get_endpoint(self, eci: EndpointCallInfo):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="get",
            endpoint=NOTIFICATIONS_ENDPOINT,
            headers=eci.authorization_header,
            expected_json_content=eci.expected_json_content,
            expected_schema=SchemaConfigs.NOTIFICATIONS_GET.value.output_schema,
            query_params=eci.query_parameters,
        )

    def follow_location(self, eci: EndpointCallInfo):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="post",
            endpoint=USER_FOLLOW_LOCATION_ENDPOINT,
            headers=eci.authorization_header,
            expected_json_content=eci.expected_json_content,
            expected_schema=SchemaConfigs.USER_FOLLOW_LOCATION.value.output_schema,
        )
