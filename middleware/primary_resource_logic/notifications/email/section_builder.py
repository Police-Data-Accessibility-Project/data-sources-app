from dataclasses import dataclass

from dominate.tags import h1, p, div, ul, li, a, br

from db.dtos.event_info import EventInfo


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
