"""
This module handles the middleware functionality for interfacing with Github issues
"""

from http import HTTPStatus

from flask import Response
from requests import request

from database_client.DTOs import DataRequestInfoForGithub
from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from middleware.access_logic import AccessInfoPrimary
from middleware.common_response_formatting import message_response
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.primary_resource_schemas.github_issue_app_schemas import (
    GithubDataRequestsIssuesPostDTO,
    GithubIssueURLInfosSchema,
    GithubIssueURLInfosDTO,
)
from middleware.third_party_interaction_logic.github_issue_api_logic import (
    create_github_issue,
    GithubIssueProjectInfo,
    get_github_issue_project_statuses,
    GithubIssueInfo,
)


def get_github_issue_title(submission_notes: str) -> str:
    if len(submission_notes) > 50:
        return f"{submission_notes[0:50]}..."
    return submission_notes


def get_github_issue_body(submission_notes: str, data_requirements: str) -> str:
    full_text = f"Submission Notes: {submission_notes}\n\nData Requirements:\n{data_requirements}"
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

    # Add each data request as a GitHub issue
    github_issue_infos = []
    for data_request in data_requests:
        github_issue_info = create_github_issue(
            title=get_github_issue_title(
                submission_notes=data_request.title,
            ),
            body=get_github_issue_body(
                submission_notes=data_request.submission_notes,
                data_requirements=data_request.data_requirements,
            ),
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


def synchronize_github_issues_with_data_requests(
    db_client: DatabaseClient, access_info: AccessInfoPrimary
) -> Response:
    """
    Synchronizes github issues with data requests
    :param db_client: DatabaseClient object
    :param access_info: AccessInfo object
    :return: A response object
    """
    requests_added: list[GithubIssueInfo] = add_ready_data_requests_as_github_issues(
        db_client
    )

    # Get all data requests with issues in the database

    github_issue_response_infos = [
        GithubIssueURLInfosDTO(
            data_request_id=request_added.data_request_id,
            github_issue_url=request_added.url,
        )
        for request_added in requests_added
    ]

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
        request_status = gipi.get_project_status(issue_number=dri.github_issue_number)
        if request_status == dri.request_status:
            continue

        db_client.update_data_request(
            entry_id=dri.data_request_id,
            column_edit_mappings={"request_status": request_status.value},
        )

        requests_updated += 1

    return message_response(
        message=f"Added {len(requests_added)} data requests to GitHub. "
        f"Updated {requests_updated} data requests in database.",
        status_code=HTTPStatus.OK,
        issues_created=[info.model_dump() for info in github_issue_response_infos],
    )
