from db.enums import RequestStatus
from middleware.enums import RecordTypes
from middleware.third_party_interaction_logic.github.issue_project_info.model import (
    GIPIInfo,
)


class GithubIssueProjectInfo:

    def __init__(self):
        self.issue_number_to_info: dict[int, GIPIInfo] = {}

    def add_info(self, issue_number: int, gipi_info: GIPIInfo):
        if issue_number in self.issue_number_to_info:
            if (
                self.issue_number_to_info[issue_number].project_status
                == gipi_info.project_status
            ):
                return
            raise ValueError(
                f"Issue number with conflicting status {issue_number}: "
                f"{gipi_info.project_status} vs {self.issue_number_to_info[issue_number]}"
            )
        self.issue_number_to_info[issue_number] = gipi_info

    def get_info(self, issue_number: int) -> GIPIInfo:
        return self.issue_number_to_info[issue_number]

    def get_project_status(self, issue_number: int) -> RequestStatus:
        try:
            gipi_info = self.issue_number_to_info[issue_number]
            return RequestStatus(gipi_info.project_status)
        except KeyError:
            raise ValueError(f"Unknown issue number {issue_number}")

    def get_labels(self, issue_number: int) -> list[RecordTypes]:
        try:
            gipi_info = self.issue_number_to_info[issue_number]
            return gipi_info.record_types
        except KeyError:
            raise ValueError(f"Unknown issue number {issue_number}")
