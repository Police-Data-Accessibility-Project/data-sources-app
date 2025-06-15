from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.base import AuthenticationInfo
from middleware.decorators.endpoint_info import endpoint_info
from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.primary_resource_logic.github_issue_app import (
    synchronize_github_issues_with_data_requests,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_github = create_namespace(namespace_attributes=AppNamespaces.GITHUB)


@namespace_github.route("/data-requests/synchronize")
class GithubDataRequestsSynchronize(PsycopgResource):

    @endpoint_info(
        namespace=namespace_github,
        auth_info=AuthenticationInfo(
            allowed_access_methods=[AccessTypeEnum.JWT],
            restrict_to_permissions=[PermissionsEnum.GITHUB_SYNC],
        ),
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
