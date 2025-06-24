from middleware.column_permission.mapping import ROLE_COLUMN_PERMISSIONS


def create_column_permissions_string_table(relation: str) -> str:
    permissions = ROLE_COLUMN_PERMISSIONS[relation]
    # Get all unique roles
    roles = sorted({role for perms in permissions.values() for role in perms})

    # Create the header row
    header = "| associated_column | " + " | ".join(roles) + " |"
    separator = "|---" + "|---" * len(roles) + "|"

    # Create rows for each associated column
    rows = []
    for column, perms in permissions.items():
        row = (
            f"| {column} | "
            + " | ".join(perms.get(role, "NONE") for role in roles)
            + " |"
        )
        rows.append(row)

    # Combine everything into a markdown table
    markdown_table = "\n".join([header, separator] + rows)
    return markdown_table
