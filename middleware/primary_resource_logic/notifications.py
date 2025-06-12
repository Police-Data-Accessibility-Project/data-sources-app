from dataclasses import dataclass
from http import HTTPStatus

from flask import Response
from pydantic import BaseModel
from werkzeug.exceptions import InternalServerError

from db.client import DatabaseClient
from db.enums import EventType
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.custom_dataclasses import EventInfo, EventBatch
from middleware.flask_response_manager import FlaskResponseManager
import dominate
from dominate.tags import *

from middleware.third_party_interaction_logic.mailgun import send_via_mailgun
from middleware.util.env import get_env_variable


class NotificationEmailContent(BaseModel):
    html_text: str
    base_text: str


DATA_REQUEST_SUBDIRECTORY = "data-request"
DATA_SOURCE_SUBDIRECTORY = "data-source"
PROFILE_SUBDIRECTORY = "profile"


@dataclass
class SectionBuilder:
    title: str
    introductory_paragraph: str
    url_base: str
    events: list[EventInfo]

    def build_html_list(
        self,
    ):
        """
        Must operate within a dominate document
        :return:
        """

        h1(self.title)
        p(self.introductory_paragraph)
        with div().add(ul()):
            for event in self.events:
                li(a(event.entity_name, href=f"{self.url_base}/{event.entity_id}"))
        br()

    def build_text_list(self) -> str:
        bullet_entries = []
        for event in self.events:
            bullet_entries.append(
                f'\t- "{event.entity_name}" at {self.url_base}/{event.entity_id}'
            )
        bullet_string = "\n".join(bullet_entries)
        return f"""
{self.title}
{self.introductory_paragraph}
{bullet_string}"""


class URLBuilder:
    """
    Builds URLs from a domain
    """

    def __init__(self, domain: str):
        self.domain = domain

    def build_url(self, subdirectory: str) -> str:
        return f"{self.domain}/{subdirectory}"


class SingularPluralWordGetter:

    def __init__(self, items: list):
        self.is_plural = len(items) != 1

    def get_word(self, singular: str, plural: str) -> str:
        if self.is_plural:
            return plural
        return singular

    def get_past_tense_to_be(self):
        if self.is_plural:
            return "were"
        return "was"


class NotificationEmailBuilder:

    def __init__(self, event_batch: EventBatch):
        if len(event_batch.events) == 0:
            raise ValueError(f"No events in batch for user {event_batch.user_id}")

        self.url_builder = URLBuilder(domain=get_env_variable("VITE_VUE_APP_BASE_URL"))
        self.email = event_batch.user_email
        self.user_id = event_batch.user_id
        self.data_request_started_events = event_batch.get_events_of_type(
            EventType.REQUEST_READY_TO_START
        )
        self.data_request_completed_events = event_batch.get_events_of_type(
            EventType.REQUEST_COMPLETE
        )
        self.data_source_approved_events = event_batch.get_events_of_type(
            EventType.DATA_SOURCE_APPROVED
        )

    def get_section_builders(self) -> list[SectionBuilder]:
        section_builders = []

        if len(self.data_source_approved_events) > 0:
            sp = SingularPluralWordGetter(self.data_source_approved_events)
            data_source_name = sp.get_word(
                singular="Data Source", plural="Data Sources"
            )
            ptb = sp.get_past_tense_to_be()
            section_builders.append(
                SectionBuilder(
                    title=f"New {data_source_name}",
                    introductory_paragraph=f"The following {data_source_name.lower()} {ptb} approved:",
                    url_base=self.url_builder.build_url(DATA_SOURCE_SUBDIRECTORY),
                    events=self.data_source_approved_events,
                )
            )

        if len(self.data_request_completed_events) > 0:
            sp = SingularPluralWordGetter(self.data_request_completed_events)
            data_request_name = sp.get_word(
                singular="Data Request", plural="Data Requests"
            )
            ptb = sp.get_past_tense_to_be()
            section_builders.append(
                SectionBuilder(
                    title=f"{data_request_name} Completed",
                    introductory_paragraph=f"The following {data_request_name.lower()} {ptb} completed:",
                    url_base=self.url_builder.build_url(DATA_REQUEST_SUBDIRECTORY),
                    events=self.data_request_completed_events,
                )
            )

        if len(self.data_request_started_events) > 0:
            sp = SingularPluralWordGetter(self.data_request_started_events)
            data_request_name = sp.get_word(
                singular="Data Request", plural="Data Requests"
            )
            ptb = sp.get_past_tense_to_be()
            section_builders.append(
                SectionBuilder(
                    title=f"{data_request_name} Started",
                    introductory_paragraph=f"The following {data_request_name.lower()} {ptb} started:",
                    url_base=self.url_builder.build_url(DATA_REQUEST_SUBDIRECTORY),
                    events=self.data_request_started_events,
                )
            )

        return section_builders

    def build_email_content(self) -> NotificationEmailContent:
        return NotificationEmailContent(
            html_text=self.build_html_text(), base_text=self.build_base_text()
        )

    def build_base_text(self):
        base_text_sections = []
        for section_builder in self.get_section_builders():
            base_text_sections.append(section_builder.build_text_list())
        base_sections_text = "\n\n".join(base_text_sections)
        base_main_text = f"""
Greetings from the Police Data Access Point! 

There have been updates to locations you've followed since we last sent notifications.
        
{base_sections_text}

Click here to view and update your followed locations: {self.url_builder.build_url(PROFILE_SUBDIRECTORY)}
"""
        return base_main_text

    def build_html_text(self):
        doc = dominate.document(title="Notifications")
        with doc:
            p("Greetings from the Police Data Access Point!")
            p(
                "There have been updates to locations you've followed since we last sent notifications."
            )
            br()
            for section_builder in self.get_section_builders():
                section_builder.build_html_list()
            p(
                "Click ",
                a("here", href=self.url_builder.build_url(PROFILE_SUBDIRECTORY)),
                " to view and update your followed locations.",
            )
        html_text = doc.render()
        return html_text


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
            raise InternalServerError(
                f"Error sending notification for event batch for user {next_event_batch.user_id}: "
                f"{e}. Sent {count} batches prior to this error."
            )

    db_client.add_to_notification_log(user_count=count)
    return FlaskResponseManager.make_response(
        data={"message": "Notifications sent successfully.", "count": count}
    )
