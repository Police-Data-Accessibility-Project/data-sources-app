import dominate
from dominate.tags import p, br, a

from db.enums import EventType
from db.dtos.event_batch import EventBatch
from middleware.primary_resource_logic.notifications.constants import (
    DATA_SOURCE_SUBDIRECTORY,
    DATA_REQUEST_SUBDIRECTORY,
    PROFILE_SUBDIRECTORY,
)
from middleware.primary_resource_logic.notifications.email.content import (
    NotificationEmailContent,
)
from middleware.primary_resource_logic.notifications.email.section_builder import (
    SectionBuilder,
)
from middleware.primary_resource_logic.notifications.url_builder import URLBuilder
from middleware.primary_resource_logic.notifications.word_getter import (
    SingularPluralWordGetter,
)
from middleware.util.env import get_env_variable


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
