from middleware.access_logic import AccessInfo, AuthenticationInfo
from middleware.decorators import endpoint_info_2
from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.primary_resource_logic.notifications_logic import send_notifications
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_notifications = create_namespace(
    namespace_attributes=AppNamespaces.NOTIFICATIONS
)


@namespace_notifications.route("")
class Notifications(PsycopgResource):

    @endpoint_info_2(
        namespace=namespace_notifications,
        auth_info=AuthenticationInfo(
            allowed_access_methods=[AccessTypeEnum.JWT],
            restrict_to_permissions=[PermissionsEnum.NOTIFICATIONS],
        ),
        schema_config=SchemaConfigs.NOTIFICATIONS_POST,
        response_info=ResponseInfo(
            success_message="Notifications sent.",
        ),
        description="Sends notifications to all users.",
    )
    def post(self, access_info: AccessInfo):
        """
        Sends notification to all users.
        This endpoint will pull qualifying events for locations which users have subscribed to
        And send updates on those events to the users that are subscribed to those events.

        Qualifying events include:
        * A data source associated with a followed location is approved
        * A data request associated with a followed location is started
        * A data request associated with a followed location is completed
        Note that in this case, "followed location" includes both the location followed
        as well as any locations which are subdivisions of the location
        (i.e. counties and localities for states, localities for counties).

        This endpoint, as designed, will send notifications for qualifying events that occurred
        in the month prior to the month in which the endpoint was called.

        :param access_info:
        :return:
        """
        return self.run_endpoint(
            wrapper_function=send_notifications,
            access_info=access_info,
        )