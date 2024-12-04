from middleware.access_logic import WRITE_ONLY_AUTH_INFO
from middleware.decorators import endpoint_info
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_batch = create_namespace(AppNamespaces.BATCH)


@namespace_batch.route("/agencies")
class AgenciesBatch(PsycopgResource):

    @endpoint_info(
        namespace=namespace_batch,
        auth_info=WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.BATCH_POST,
        response_info=ResponseInfo(
            success_message="At least some resources created successfully."
        ),
    )
    def post(self):
        pass
