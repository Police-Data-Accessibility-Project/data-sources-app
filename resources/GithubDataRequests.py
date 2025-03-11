from middleware.access_logic import AccessInfoPrimary, WRITE_ONLY_AUTH_INFO
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.github_issue_app_logic import (
    synchronize_github_issues_with_data_requests,
)
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_github = create_namespace(namespace_attributes=AppNamespaces.GITHUB)


@namespace_github.route("/data-requests/synchronize")
class GithubDataRequestsSynchronize(PsycopgResource):

    @endpoint_info(
        namespace=namespace_github,
        auth_info=WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.GITHUB_DATA_REQUESTS_SYNCHRONIZE_POST,
        response_info=ResponseInfo(
            success_message="Data requests successfully synchronized."
        ),
        description="Synchronizes Github issues with the database",
    )
    def post(self, access_info: AccessInfoPrimary):
        """
        Synchronizes the status of Github issues with their representation in the database
        """
        return self.run_endpoint(
            wrapper_function=synchronize_github_issues_with_data_requests,
            access_info=access_info,
        )
