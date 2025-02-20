"""
This script uses the Github Client to extract issues from recent PRs into Dev that have not yet been merged into main
It then outputs the issues to stdout for use in the next step
"""

import subprocess
import json
import re

PATTERN = r"https:\/\/github\.com\/Police\-Data\-Accessibility\-Project\/data\-sources\-app\/issues\/\d+"

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

text = result.stdout
json_text = json.loads(text)

issue_urls = []

for issue in json_text:
    body = issue["body"]
    issues_in_body = re.findall(PATTERN, body)
    issue_urls.extend(issues_in_body)

# Remove duplicates
issue_urls = list(set(issue_urls))

# Sort
issue_urls.sort()

issue_string = " * " + "\n * ".join(issue_urls)

result = subprocess.run(
    [
        "gh",
        "pr",
        "edit",
        "${{ github.event.pull_request.number }}",
        "--body",
        '"$NEW_BODY"',
    ],
    capture_output=True,
    text=True,
)
print(result.stderr)


print(issue_string)
