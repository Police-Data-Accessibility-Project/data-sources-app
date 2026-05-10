"""Tests for cursor-based pagination of GitHub GraphQL queries.

These tests verify that paginated helpers correctly issue an initial query and
then continue requesting additional pages while ``hasNextPage`` is true,
threading the ``endCursor`` through as the ``after`` argument.

Issue: https://github.com/Police-Data-Accessibility-Project/data-sources-app/issues/675
"""

from unittest.mock import patch

from middleware.third_party_interaction_logic.github.helpers import (
    convert_graph_ql_result_to_issue_info,
    get_github_issue_project_statuses,
)
from middleware.third_party_interaction_logic.github.label_manager import (
    GithubLabelManager,
)


def _make_project_items_response(
    nodes: list[dict], end_cursor: str | None, has_next_page: bool
) -> dict:
    return {
        "data": {
            "organization": {
                "projectV2": {
                    "title": "Test Project",
                    "items": {
                        "pageInfo": {
                            "endCursor": end_cursor,
                            "hasNextPage": has_next_page,
                        },
                        "nodes": nodes,
                    },
                }
            }
        }
    }


def _project_node(issue_number: int, status: str = "Active") -> dict:
    return {
        "content": {
            "number": issue_number,
            "title": f"Issue {issue_number}",
            "labels": {"nodes": []},
        },
        "fieldValueByName": {"name": status},
    }


def test_get_github_issue_project_statuses_paginates_until_no_next_page():
    """When hasNextPage is true, the helper should issue another query
    with the ``after`` cursor and merge the resulting nodes."""
    page_1 = _make_project_items_response(
        nodes=[_project_node(1), _project_node(2)],
        end_cursor="cursor-1",
        has_next_page=True,
    )
    page_2 = _make_project_items_response(
        nodes=[_project_node(3)],
        end_cursor="cursor-2",
        has_next_page=False,
    )

    with patch(
        "middleware.third_party_interaction_logic.github.helpers.make_graph_ql_query"
    ) as mock_query:
        mock_query.side_effect = [page_1, page_2]
        gipi = get_github_issue_project_statuses([1, 2, 3])

    assert mock_query.call_count == 2
    # Second call should include the cursor from the first response.
    second_call_query = mock_query.call_args_list[1].kwargs["query"]
    assert 'after: "cursor-1"' in second_call_query

    # All issues across both pages should be merged into the result.
    assert {1, 2, 3} <= set(gipi.issue_number_to_info.keys())


def test_get_github_issue_project_statuses_single_page_no_extra_calls():
    """If the first page has hasNextPage=false, no further calls are made."""
    page = _make_project_items_response(
        nodes=[_project_node(1)],
        end_cursor=None,
        has_next_page=False,
    )

    with patch(
        "middleware.third_party_interaction_logic.github.helpers.make_graph_ql_query"
    ) as mock_query:
        mock_query.return_value = page
        gipi = get_github_issue_project_statuses([1])

    assert mock_query.call_count == 1
    assert 1 in gipi.issue_number_to_info


def test_convert_graph_ql_result_to_issue_info_merges_pages():
    """convert_graph_ql_result_to_issue_info should accept multiple page
    payloads and merge their nodes."""
    page_1 = _make_project_items_response(
        nodes=[_project_node(10), _project_node(11)],
        end_cursor="c1",
        has_next_page=True,
    )
    page_2 = _make_project_items_response(
        nodes=[_project_node(12)],
        end_cursor="c2",
        has_next_page=False,
    )

    gipi = convert_graph_ql_result_to_issue_info([page_1, page_2])
    assert {10, 11, 12} <= set(gipi.issue_number_to_info.keys())


def test_label_manager_paginates_labels():
    """GithubLabelManager.get_labels should follow the labels pageInfo
    cursor across multiple pages."""
    page_1 = {
        "data": {
            "repository": {
                "labels": {
                    "pageInfo": {"endCursor": "lc-1", "hasNextPage": True},
                    "nodes": [
                        {"id": "id-a", "name": "label-a"},
                        {"id": "id-b", "name": "label-b"},
                    ],
                }
            }
        }
    }
    page_2 = {
        "data": {
            "repository": {
                "labels": {
                    "pageInfo": {"endCursor": "lc-2", "hasNextPage": False},
                    "nodes": [{"id": "id-c", "name": "label-c"}],
                }
            }
        }
    }

    with patch(
        "middleware.third_party_interaction_logic.github.label_manager."
        "make_graph_ql_query"
    ) as mock_query:
        mock_query.side_effect = [page_1, page_2]
        manager = GithubLabelManager()

    assert mock_query.call_count == 2
    second_call_query = mock_query.call_args_list[1].kwargs["query"]
    assert 'after: "lc-1"' in second_call_query
    assert manager.label_name_to_id == {
        "label-a": "id-a",
        "label-b": "id-b",
        "label-c": "id-c",
    }
