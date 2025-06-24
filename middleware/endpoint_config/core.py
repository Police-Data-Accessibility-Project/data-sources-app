from pydantic import BaseModel

from endpoints._helpers.response_info import ResponseInfo
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.config.core import EndpointSchemaConfig
from middleware.security.auth.info.base import AuthenticationInfo


# TODO: Work in progress, yet to be incorporated
class EndpointConfig(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    route: str
    resource: PsycopgResource
    auth: AuthenticationInfo
    schema: EndpointSchemaConfig
    response: ResponseInfo
    description: str
