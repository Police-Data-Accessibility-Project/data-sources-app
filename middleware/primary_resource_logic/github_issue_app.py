"""
This module handles the middleware functionality for interfacing with Github issues
"""

from http import HTTPStatus
from typing import Optional

from flask import Response

from db.DTOs import DataRequestInfoForGithub
from db.client import DatabaseClient
from db.enums import RequestStatus
from middleware.access_logic import AccessInfoPrimary
from middleware.common_response_formatting import message_response
from middleware.enums import RecordTypes
from middleware.schema_and_dto_logic.primary_resource_schemas.github_issue_app_schemas import (
    GithubIssueURLInfosDTO,
)
from middleware.third_party_interaction_logic.github_issue_api_logic import (
    GithubIssueProjectInfo,
    get_github_issue_project_statuses,
    GithubIssueInfo,
    GithubIssueManager,
)


def get_github_issue_title(submission_notes: str) -> str:
    if len(submission_notes) > 50:
        return f"{submission_notes[0:50]}..."
    return submission_notes


def get_github_issue_body(
    submission_notes: str, data_requirements: str, locations: Optional[list[str]]
) -> str:
    if locations is not None:
        locations_str = "## Locations: \n * " + "\n * ".join(locations)
    else:
        locations_str = ""

    full_text = (
        f"## Submission Notes: \n{submission_notes}\n\n"
        f"## Data Requirements:\n{data_requirements}\n\n"
        f"{locations_str}"
    )
    return full_text


def add_ready_data_requests_as_github_issues(
    db_client: DatabaseClient,
) -> list[GithubIssueInfo]:
    """
    Adds all data requests marked as 'Ready to Start' to Github
    Returns the number of data requests added
    """
    # Get data requests marked as 'Ready to Start' and lacking a GitHub issue URL
    data_requests: list[DataRequestInfoForGithub] = (
        db_client.get_data_requests_ready_to_start_without_github_issue()
    )
    if len(data_requests) == 0:
        return []

    gim = GithubIssueManager()
    # Add each data request as a GitHub issue
    github_issue_infos = []
    for data_request in data_requests:
        github_issue_info = gim.create_issue_with_status(
            title=get_github_issue_title(
                submission_notes=data_request.title,
            ),
            body=get_github_issue_body(
                submission_notes=data_request.submission_notes,
                data_requirements=data_request.data_requirements,
                locations=data_request.locations,
            ),
            status=RequestStatus.READY_TO_START,
            record_types=data_request.record_types or [],
        )

        # Update the data request with the github issue url
        db_client.create_data_request_github_info(
            column_value_mappings={
                "data_request_id": data_request.id,
                "github_issue_url": github_issue_info.url,
                "github_issue_number": github_issue_info.number,
            },
        )
        github_issue_info.data_request_id = data_request.id
        github_issue_infos.append(github_issue_info)

    return github_issue_infos


def is_empty(a: Optional[list]) -> bool:
    return a is None or len(a) == 0


def record_types_match(
    record_types_required_str: Optional[list[str]],
    record_types_enums: Optional[list[RecordTypes]],
) -> bool:
    if is_empty(record_types_required_str) and is_empty(record_types_enums):
        return True
    if not is_empty(record_types_required_str) and is_empty(record_types_enums):
        return False
    if is_empty(record_types_required_str) and not is_empty(record_types_enums):
        return False
    record_types_str = [record_type.value for record_type in record_types_enums]
    return set(record_types_required_str) == set(record_types_str)


def synchronize_github_issues_with_data_requests(
    db_client: DatabaseClient, access_info: Optional[AccessInfoPrimary]
) -> Response:
    """
    Synchronizes github issues with data requests
    :param db_client: DatabaseClient object
    :param access_info: AccessInfo object
    :return: A response object
    """

    # Get all data requests with issues in the database
    data_requests_with_issues: list[db_client.DataRequestIssueInfo] = (
        db_client.get_unarchived_data_requests_with_issues()
    )
    issue_numbers = [dri.github_issue_number for dri in data_requests_with_issues]

    # Get the project statuses of these issues
    gipi: GithubIssueProjectInfo = get_github_issue_project_statuses(
        issue_numbers=issue_numbers
    )

    # Update in the database data requests whose GitHub issue status has changed
    requests_updated = 0
    for dri in data_requests_with_issues:
        gipi_info = gipi.get_info(issue_number=dri.github_issue_number)
        request_status = gipi.get_project_status(issue_number=dri.github_issue_number)
        record_types_required = dri.record_types_required
        if request_status == dri.request_status and record_types_match(
            record_types_required, gipi_info.record_types
        ):
            continue

        db_client.update_data_request(
            entry_id=dri.data_request_id,
            column_edit_mappings={
                "request_status": request_status.value,
                "record_types_required": gipi_info.record_types_as_list_of_strings(),
            },
        )

        requests_updated += 1

    # Add data requests to GitHub
    requests_added: list[GithubIssueInfo] = add_ready_data_requests_as_github_issues(
        db_client
    )

    github_issue_response_infos = [
        GithubIssueURLInfosDTO(
            data_request_id=request_added.data_request_id,
            github_issue_url=request_added.url,
        )
        for request_added in requests_added
    ]

    return message_response(
        message=f"Added {len(requests_added)} data requests to GitHub. "
        f"Updated {requests_updated} data requests in database.",
        status_code=HTTPStatus.OK,
        issues_created=[info.model_dump() for info in github_issue_response_infos],
    )
