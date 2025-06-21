# pyright: reportUninitializedInstanceVariable=false
from sqlalchemy.orm import Mapped

from db.models.mixins import DataRequestIDMixin
from db.models.templates.standard import StandardBase
from middleware.enums import Relations


class DataRequestsGithubIssueInfo(StandardBase, DataRequestIDMixin):
    __tablename__ = Relations.DATA_REQUESTS_GITHUB_ISSUE_INFO.value

    github_issue_url: Mapped[str]
    github_issue_number: Mapped[int]
