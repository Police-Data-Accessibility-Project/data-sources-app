from middleware.access_logic import AccessInfo, WRITE_ONLY_AUTH_INFO
from middleware.decorators import endpoint_info_2
from middleware.primary_resource_logic.github_issue_app_logic import add_data_request_as_github_issue
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_github = create_namespace(
    namespace_attributes=AppNamespaces.GITHUB
)

@namespace_github.route("/data-requests/<data_request_id>/issues")
class GithubIssues(PsycopgResource):

    @endpoint_info_2(
        namespace=namespace_github,
        auth_info=WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.GITHUB_DATA_REQUESTS_ISSUES_POST,
        response_info=ResponseInfo(
            success_message="Returns the id of the newly created issue."
        ),
        description="Create  GitHub issue for data request",
    )
    def post(self, data_request_id: int, access_info: AccessInfo):
        """
        Creates a GitHub issue for a data request, if it does not already exist
        """
        return self.run_endpoint(
            wrapper_function=add_data_request_as_github_issue,
            schema_populate_parameters=SchemaConfigs.GITHUB_DATA_REQUESTS_ISSUES_POST.value.get_schema_populate_parameters(),
            access_info=access_info,
        )