from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.decorators.endpoint_info import endpoint_info
from middleware.primary_resource_logic.notifications.notifications import (
    send_notifications,
    preview_notifications,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from middleware.security.auth.info.instantiations import NOTIFICATIONS_AUTH_INFO
from utilities.namespace import create_namespace, AppNamespaces

namespace_notifications = create_namespace(
    namespace_attributes=AppNamespaces.NOTIFICATIONS
)


@namespace_notifications.route("")
class Notifications(PsycopgResource):
    @endpoint_info(
        namespace=namespace_notifications,
        auth_info=NOTIFICATIONS_AUTH_INFO,
        schema_config=SchemaConfigs.NOTIFICATIONS_POST,
        response_info=ResponseInfo(
            success_message="Notifications sent.",
        ),
        description="Sends notifications about events to users following their associated locations.",
    )
    def post(self, access_info: AccessInfoPrimary):
        """
        Sends notification to all users.
        This endpoint will pull qualifying events for locations which users have subscribed to
        And send updates on those events to the associated users

        Qualifying events include:
        * A data source associated with a followed location is approved
        * A data request associated with a followed location is started
        * A data request associated with a followed location is completed

        Note that "followed location" includes both the location explicitly followed by the user
        as well as any locations which are subdivisions of the location followed
        (i.e. counties and localities for states, localities for counties).

        This endpoint, as designed, will send notifications for qualifying events that occurred
        in the month *prior to the month* in which the endpoint was called.

        :param access_info:
        :return:
        """
        return self.run_endpoint(
            wrapper_function=send_notifications,
            access_info=access_info,
        )


@namespace_notifications.route("/preview")
class NotificationsPreview(PsycopgResource):
    @endpoint_info(
        namespace=namespace_notifications,
        auth_info=NOTIFICATIONS_AUTH_INFO,
        schema_config=SchemaConfigs.NOTIFICATIONS_PREVIEW,
        response_info=ResponseInfo(
            success_message="Preview retrieved.",
        ),
        description="Previews notification metrics without sending them.",
    )
    def get(self, access_info: AccessInfoPrimary):
        """Previews notification metrics."""
        return self.run_endpoint(
            wrapper_function=preview_notifications,
            access_info=access_info,
        )
