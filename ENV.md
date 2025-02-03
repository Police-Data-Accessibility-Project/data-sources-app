In both the local root directory and the `/client` directory, either:
1. Either add a `.env` file to your local root directory with the below secrets
2. or manually export the below secrets

Reach out to contact@pdap.io or make noise in Discord if you'd like access to these keys.


| Name                                  | Description                                                                                                       | Example                                              |
|---------------------------------------|-------------------------------------------------------------------------------------------------------------------|------------------------------------------------------|
| DO_DATABASE_URL                       | Used to connect to the database.                                                                                  | `postgres://data_sources_app:<password>@db-url`     |
| VITE_VUE_API_BASE_URL                 | The base URL for the API.                                                                                         | `http://localhost:5000`                             |
| VITE_VUE_APP_BASE_URL                 | The base URL for the UI.                                                                                          | `http://localhost:8888`                             |
| VITE_ADMIN_API_KEY                    | Used as the `Basic` auth token for the web client. Must be in `/client` directory `.env` file.                    | `1234abcd`                                          |
| GH_CLIENT_ID                          | Used to authenticate with GitHub via OAuth. Must correspond to the `client_id` provided by GitHub.                | `GithubProvidedClientId`                            |
| GH_CLIENT_SECRET                      | Used to authenticate with GitHub via OAuth. Must correspond to the `client_secret` provided by GitHub.            | `GithubProvidedClientSecret`                        |
| JWT_SECRET_KEY                        | Used to sign and verify JWT tokens. Ensures JWT tokens are recognizable by this version of the app.               | `myCustomJwtSecretKey`                              |
| RESET_PASSWORD_SECRET_KEY             | Used to sign and verify JWT tokens for the reset password feature.                                                | `myCustomResetPasswordSecretKey`                    |
| FLASK_APP_COOKIE_ENCRYPTION_KEY       | Used to create signed cookies to prevent CSRF attacks.                                                            | `myCustomFlaskAppSecretKey`                         |
| DEVELOPMENT_PASSWORD                  | Used to create a test user with elevated permissions for testing.                                                  | `myCustomDevelopmentPassword`                       |
| GH_API_ACCESS_TOKEN                   | Used to authenticate with GitHub when adding or retrieving information about GitHub Issues.                        | `GithubProvidedAccessToken`                         |
| GH_ISSUE_REPO_NAME                    | Identifies the repository where issues will be created and retrieved.                                              | `github-username/github-repo-name`                  |
| VALIDATE_EMAIL_SECRET_KEY             | Used to sign and verify JWT tokens for email validation.                                                           | `myCustomValidateEmailSecretKey`                    |
| VITE_V2_FEATURE_ENHANCED_SEARCH       | Feature flag: 'enabled' shows enhanced search features, 'disabled' hides them.                                     | `enabled` or `disabled`                             |
| VITE_V2_FEATURE_AUTHENTICATE          | Feature flag: 'enabled' allows sign-in/sign-out, 'disabled' disallows.                                             | `enabled` or `disabled`                             |
| VITE_V2_FEATURE_CREATE_RECORDS        | Feature flag: 'enabled' allows users to create data sources and requests in-app, 'disabled' redirects to Airtable. | `enabled` or `disabled`                             |

Additionally, if you are testing the email functionality, you will need to also provide the `MAILGUN_KEY` environment variable as well (also obtainable from the sources mentioned above).

#### .env Example
```
# .env

DO_DATABASE_URL="postgres://data_sources_app:<password>@db-postgresql-nyc3-38355-do-user-8463429-0.c.db.ondigitalocean.com:25060/defaultdb"

```

#### Shell Example
```shell
# shell

export DO_DATABASE_URL=postgres://data_sources_app:<password>@db-postgresql-nyc3-38355-do-user-8463429-0.c.db.ondigitalocean.com:25060/defaultdb
# etc.
```