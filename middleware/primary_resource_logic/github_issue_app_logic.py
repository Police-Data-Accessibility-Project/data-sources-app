"""
This module handles the middleware functionality for interfacing with Github issues
"""
from http import HTTPStatus

from flask import Response
from requests import request

from database_client.database_client import DatabaseClient
from database_client.db_client_dataclasses import WhereMapping
from middleware.access_logic import AccessInfo
from middleware.common_response_formatting import message_response
from middleware.schema_and_dto_logic.primary_resource_schemas.github_issue_app_schemas import \
    GithubDataRequestsIssuesPostDTO
from middleware.third_party_interaction_logic.github_issue_api_logic import create_github_issue, GithubIssueProjectInfo, \
    get_github_issue_project_statuses


def get_github_issue_title(submission_notes: str) -> str:
    if len(submission_notes) > 50:
        return f"{submission_notes[0:50]}..."
    return submission_notes

def get_github_issue_body(submission_notes: str, data_requirements: str) -> str:
    full_text = f"Submission Notes: {submission_notes}\n\nData Requirements:\n{data_requirements}"
    return full_text

def add_data_request_as_github_issue(
    db_client: DatabaseClient,
    access_info: AccessInfo,
    dto: GithubDataRequestsIssuesPostDTO
) -> Response:
    """
    Adds a data request as a github issue
    :param db_client: DatabaseClient object
    :param data_request_id: The id of the data request
    :param github_issue_url: The url of the github issue
    :return: A response object
    """

    # Check that the data request doesn't already have an issue url
    data_request_info = db_client.get_data_requests(
        columns = ["github_issue_url", "submission_notes", "data_requirements"],
        where_mappings = WhereMapping.from_dict({
            "id": int(dto.data_request_id)
        })
    )[0]

    if data_request_info["github_issue_url"] is not None:
        return message_response(
            message="Data Request already has an associated Github Issue.",
            status_code=HTTPStatus.CONFLICT,
            github_issue_url=data_request_info["github_issue_url"]
        )

    # Add the data request as a github issue
    github_issue_info = create_github_issue(
        title=get_github_issue_title(
            submission_notes=data_request_info["submission_notes"],
        ),
        body=get_github_issue_body(
            submission_notes=data_request_info["submission_notes"],
            data_requirements=data_request_info["data_requirements"]
        ),
    )

    # Update the data request with the github issue url
    db_client.create_data_request_github_info(
        column_value_mappings = {
            "data_request_id": dto.data_request_id,
            "github_issue_url": github_issue_info.url,
            "github_issue_number": github_issue_info.number
        }
    )

    return message_response(
        message="Issue created successfully",
        github_issue_url=github_issue_info.url
    )

def synchronize_github_issues_with_data_requests(
    db_client: DatabaseClient,
    access_info: AccessInfo
) -> Response:
    """
    Synchronizes github issues with data requests
    :param db_client: DatabaseClient object
    :param access_info: AccessInfo object
    :return: A response object
    """
    data_requests_with_issues: list[db_client.DataRequestIssueInfo] = db_client.get_unarchived_data_requests_with_issues()
    issue_numbers = [dri.github_issue_number for dri in data_requests_with_issues]

    gipi: GithubIssueProjectInfo = get_github_issue_project_statuses(issue_numbers=issue_numbers)

    requests_updated = 0
    for dri in data_requests_with_issues:
        request_status = gipi.get_project_status(issue_number=dri.github_issue_number)
        if request_status == dri.request_status:
            continue

        db_client.update_data_request(
            entry_id=dri.data_request_id,
            column_edit_mappings = {
                "request_status": request_status.value
            }
        )

        requests_updated += 1

    return message_response(
        message=f"Successfully updated {requests_updated} data requests",
        status_code=HTTPStatus.OK
    )

