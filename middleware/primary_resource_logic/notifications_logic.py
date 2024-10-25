import os
from dataclasses import dataclass
from http import HTTPStatus

from flask import Response

from database_client.database_client import DatabaseClient
from database_client.enums import EventType
from middleware.access_logic import AccessInfo
from middleware.custom_dataclasses import EventInfo, EventBatch
from middleware.flask_response_manager import FlaskResponseManager

@dataclass
class NotificationEmailContent:
    html_text: str
    base_text: str

DATA_REQUEST_SUBDIRECTORY = "data-request"
DATA_SOURCE_SUBDIRECTORY = "data-source"

@dataclass
class SectionBuilder:
    title: str
    introductory_paragraph: str
    url_base: str
    events: list[EventInfo]

    def build_html_list(
            self,
    ) -> str:
        li_entries = []
        for event in self.events:
            li_entries.append(f"<li><a href='{self.url_base}{event.entity_id}'>{event.entity_name}</a></li>")
        return f"""
            <h1>{self.title}</h1>
            <p>{self.introductory_paragraph}</p>
            <ul>
                {"".join(li_entries)}
            </ul>
            </br>
        """

    def build_text_list(
        self
    ) -> str:
        bullet_entries = []
        for event in self.events:
            bullet_entries.append(f"- {event.entity_name} at {self.url_base}{event.entity_id}")
        return f"""
    {self.title}
    {self.introductory_paragraph}
    {"".join(bullet_entries)}

    """

class URLBuilder:
    """
    Builds URLs from a domain
    """
    def __init__(self, domain: str):
        self.domain = domain

    def build_url(self, subdirectory: str) -> str:
        return f"{self.domain}/{subdirectory}"

class NotificationEmailBuilder:

    def __init__(self, event_batch: EventBatch):
        if len(event_batch.events) == 0:
            raise ValueError(f"No events in batch for user {event_batch.user_id}")

        self.url_base = URLBuilder(
            domain=os.environ["NOTIFICATION_URL_BASE"]
        )
        self.email = event_batch.user_email
        self.user_id = event_batch.user_id
        self.data_request_started_events = event_batch.get_events_of_type(EventType.REQUEST_READY_TO_START)
        self.data_request_completed_events = event_batch.get_events_of_type(EventType.REQUEST_COMPLETE)
        self.data_source_approved_events = event_batch.get_events_of_type(EventType.DATA_SOURCE_APPROVED)

    def get_section_builders(self) -> list[SectionBuilder]:
        section_builders = []

        if len(self.data_source_approved_events) > 0:
            section_builders.append(SectionBuilder(
                title="Data Source Approved",
                introductory_paragraph="The following data sources have been approved:",
                url_base=self.url_base.build_url(DATA_SOURCE_SUBDIRECTORY),
                events=self.data_source_approved_events
            ))

        if len(self.data_request_completed_events) > 0:
            section_builders.append(SectionBuilder(
                title="Data Request Completed",
                introductory_paragraph="The following data requests have completed:",
                url_base=self.url_base.build_url(DATA_REQUEST_SUBDIRECTORY),
                events=self.data_request_completed_events
            ))

        if len(self.data_request_started_events) > 0:
            section_builders.append(SectionBuilder(
                title="Data Request Started",
                introductory_paragraph="The following data requests have been started:",
                url_base=self.url_base.build_url(DATA_REQUEST_SUBDIRECTORY),
                events=self.data_request_started_events
            ))

        return section_builders

    def build_email_content(self) -> NotificationEmailContent:

        section_builders = self.get_section_builders()


        raise NotImplementedError


def format_and_send_notifications(
    event_batch: EventBatch,
):
    raise NotImplementedError

def send_notifications(db_client: DatabaseClient, access_info: AccessInfo) -> Response:
    """
    Sends notifications to all users.

    :param db_client: The database client.
    :param access_info: The access info.
    :return: The response.
    """
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
            FlaskResponseManager.abort(
                message=f"Error sending notification for event batch for user {next_event_batch.user_id}: {e}. Sent {count} batches prior to this error.",
                code=HTTPStatus.INTERNAL_SERVER_ERROR, )
    return FlaskResponseManager.make_response(
        data={
            "message": "Notifications sent successfully.",
            "count": count
        }
    )