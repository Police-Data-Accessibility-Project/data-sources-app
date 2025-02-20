"""
This script uses the Github Client to extract issues from recent PRs into Dev that have not yet been merged into main
It then outputs the issues to stdout for use in the next step
"""

import subprocess
import json
import re
import os

PATTERN = r"https:\/\/github\.com\/Police\-Data\-Accessibility\-Project\/data\-sources\-app\/issues\/\d+"

# Get PR number from environment variable
PR_NUMBER = os.environ.get("PR_NUMBER")

if not PR_NUMBER:
    print("No PR number found in environment. Exiting.")
    exit(1)

result = subprocess.run(
    [
        "gh",
        "pr",
        "list",
        "--base",
        "dev",
        "--state",
        "merged",
        "--json",
        "body",
    ],
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print("Error fetching PRs:", result.stderr)
    exit(1)

text = result.stdout
json_text = json.loads(text)

issue_urls = []

for issue in json_text:
    body = issue.get("body", "")
    issues_in_body = re.findall(PATTERN, body)
    issue_urls.extend(issues_in_body)

if not issue_urls:
    print("No issues found.")
    exit(0)


# Remove duplicates
issue_urls = list(set(issue_urls))

# Sort
issue_urls.sort()

issue_string = " * " + "\n * ".join(issue_urls)

new_body = "\n\n### Extracted Issues:\n" + issue_string

result = subprocess.run(
    [
        "gh",
        "pr",
        "edit",
        PR_NUMBER,
        "--body",
        new_body,
    ],
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print("Error updating PR body:", result.stderr)
    exit(1)


print("Updated PR body successfully!")
