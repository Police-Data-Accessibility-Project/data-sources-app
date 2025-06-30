# pyright: reportAttributeAccessIssue = false

from flask import Response, make_response
from werkzeug.exceptions import InternalServerError

from db.client.core import DatabaseClient
from middleware.primary_resource_logic.notifications.email.builder import (
    NotificationEmailBuilder,
)
from middleware.security.access_info.primary import AccessInfoPrimary
from db.dtos.event_batch import EventBatch

from middleware.third_party_interaction_logic.mailgun import send_via_mailgun


def format_and_send_notifications(
    event_batch: EventBatch,
):
    neb = NotificationEmailBuilder(event_batch=event_batch)
    email_content = neb.build_email_content()
    send_via_mailgun(
        to_email=event_batch.user_email,
        subject="Updates to police data sources in locations you follow",
        text=email_content.base_text,
        html=email_content.html_text,
    )


def send_notifications(
    db_client: DatabaseClient, access_info: AccessInfoPrimary
) -> Response:
    """Sends notifications to all users."""
    db_client.optionally_update_user_notification_queue()
    next_event_batch = db_client.get_next_user_event_batch()
    count = 0
    while next_event_batch is not None:
        try:
            format_and_send_notifications(event_batch=next_event_batch)
            db_client.mark_user_events_as_sent(next_event_batch.user_id)
            count += 1
            next_event_batch = db_client.get_next_user_event_batch()
        except Exception as e:
            raise InternalServerError(
                f"Error sending notification for event batch for user {next_event_batch.user_id}: "
                + f"{e}. Sent {count} batches prior to this error."
            )

    db_client.add_to_notification_log(user_count=count)
    return make_response(
        {"message": "Notifications sent successfully.", "count": count}
    )


def preview_notifications(
    db_client: DatabaseClient, access_info: AccessInfoPrimary
) -> Response:
    db_client.optionally_update_user_notification_queue()
    notifications_preview = db_client.preview_notifications()
    return make_response(notifications_preview.model_dump(mode="json"))
