# Authentication

The API supports multiple authentication methods depending on the endpoint. Each endpoint declares which methods it accepts via an `AuthenticationInfo` configuration.

## Authentication Methods

### JWT (JSON Web Token)

The primary authentication method for user-facing operations.

- **Scheme:** `Bearer` token in the `Authorization` header.
- **Access token lifetime:** 15 minutes.
- **Refresh token lifetime:** 1 day.
- **Signing key:** `JWT_SECRET_KEY` environment variable.

**Flow:**
1. User logs in via `POST /auth/login` (email + password) or via GitHub OAuth.
2. Server returns an access token and a refresh token.
3. Client includes the access token in subsequent requests: `Authorization: Bearer <token>`.
4. When the access token expires, the client calls `POST /auth/refresh-session` with the refresh token in the `Authorization` header to get a new access token.

### API Key

For programmatic / machine-to-machine access.

- **Scheme:** `Basic` auth in the `Authorization` header.
- Available on endpoints configured with `API_OR_JWT_AUTH_INFO`.

### GitHub OAuth

For user authentication via GitHub accounts.

- Uses authlib's Flask OAuth integration.
- **Flow:**
  1. Client redirects to GitHub authorization URL.
  2. GitHub redirects back to the callback URL with an authorization code.
  3. The server exchanges the code for a GitHub access token.
  4. The server creates or links a local user account and issues a JWT.

**Environment variables required:** `GH_CLIENT_ID`, `GH_CLIENT_SECRET`, `GH_CALLBACK_URL`.

### Special-Purpose Tokens

- **Reset Password Token:** Signed with `RESET_PASSWORD_SECRET_KEY`. Used only by password reset endpoints.
- **Validate Email Token:** Signed with `VALIDATE_EMAIL_SECRET_KEY`. Used only by email validation endpoints.

## Authorization (Permissions)

Endpoints can restrict access to users with specific permissions via the `restrict_to_permissions` field on `AuthenticationInfo`.

### Permission Types

Defined in `middleware/enums.py` as `PermissionsEnum`:

| Permission | Value | Purpose |
|-----------|-------|---------|
| `DB_WRITE` | `write_data` | Write access to data |
| `READ_ALL_USER_INFO` | `read_all_user_info` | Admin: read all user data |
| `NOTIFICATIONS` | `send_notifications` | Send notification events |
| `SOURCE_COLLECTOR` | `access_source_collector` | Access source collector tools |
| `USER_CREATE_UPDATE` | `create_update_user` | Admin: create/update users |
| `GITHUB_SYNC` | `sync_to_github` | Sync operations to GitHub |
| `SOURCE_COLLECTOR_FINAL_REVIEW` | `source_collector_final_review` | Final review for source collection |
| `SOURCE_COLLECTOR_DATA_SOURCES` | `call_ds_source_collector_endpoints` | Source collector data source endpoints |

### Pre-Configured Auth Profiles

Common auth configurations are defined in `middleware/security/auth/info/instantiations.py`:

| Profile | Access Methods | Permissions Required |
|---------|---------------|---------------------|
| `NO_AUTH_INFO` | None (public) | None |
| `STANDARD_JWT_AUTH_INFO` | JWT | None (any authenticated user) |
| `API_OR_JWT_AUTH_INFO` | API key or JWT | None |
| `WRITE_ONLY_AUTH_INFO` | JWT | `DB_WRITE` |
| `NOTIFICATIONS_AUTH_INFO` | JWT | `NOTIFICATIONS` |
| `READ_USER_AUTH_INFO` | JWT | `READ_ALL_USER_INFO` |
| `WRITE_USER_AUTH_INFO` | JWT | `USER_CREATE_UPDATE` |
| `RESET_PASSWORD_AUTH_INFO` | Reset password token | N/A |
| `VALIDATE_EMAIL_AUTH_INFO` | Email validation token | N/A |

### Column-Level Permissions

Beyond endpoint-level auth, the app also enforces column-level read/write permissions per role. These are configured via CSV files in `relation_access_permissions/` — see that directory's [README](../../relation_access_permissions/README.md) for details.
