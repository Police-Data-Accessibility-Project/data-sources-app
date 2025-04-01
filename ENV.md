In both the local root directory and the `/client` directory, either:
1. Either add a `.env` file to your local root directory with the below secrets
2. or manually export the below secrets

Reach out to contact@pdap.io or make noise in Discord if you'd like access to these keys.


| Name                            | Description                                                                                           | Example                                         |
| ------------------------------- |-------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| DO_DATABASE_URL                 | Used to connect to the database.                                                                      | `postgres://data_sources_app:<password>@db-url` |
| VITE_VUE_API_BASE_URL           | The base URL for the API.                                                                             | `http://localhost:5000`                         |
| VITE_VUE_APP_BASE_URL           | The base URL for the UI.                                                                              | `http://localhost:8888`                         |
| GH_CLIENT_ID                    | Used to authenticate with GitHub via OAuth. Must correspond to the `client_id` provided by GitHub.    | `GithubProvidedClientId`                        |
| GH_CLIENT_SECRET                | Used to authenticate with GitHub via OAuth. Must correspond to the `client_secret` provided by GitHub. | `GithubProvidedClientSecret`                    |
| JWT_SECRET_KEY                  | Used to sign and verify JWT tokens. Ensures JWT tokens are recognizable by this version of the app.   | `myCustomJwtSecretKey`                          |
| RESET_PASSWORD_SECRET_KEY       | Used to sign and verify JWT tokens for the reset password feature.                                    | `myCustomResetPasswordSecretKey`                |
| FLASK_APP_COOKIE_ENCRYPTION_KEY | Used to create signed cookies to prevent CSRF attacks.                                                | `myCustomFlaskAppSecretKey`                     |
| DEVELOPMENT_PASSWORD            | Used to create a test user with elevated permissions for testing.                                     | `myCustomDevelopmentPassword`                   |
| GH_API_ACCESS_TOKEN             | Used to authenticate with GitHub when adding or retrieving information about GitHub Issues.           | `GithubProvidedAccessToken`                     |
| GH_CALLBACK_URL                 | The callback URL for GitHub OAuth.                                                                     | `https://example.com/api/auth/callback`         |
| VALIDATE_EMAIL_SECRET_KEY       | Used to sign and verify JWT tokens for email validation.                                              | `myCustomValidateEmailSecretKey`                |
| WEBHOOK_URL                     | The URL where webhook events will be sent.                                                            | `https://example.com/webhook`                   |
|TEST_EMAIL_ADDRESS              | The email address to which test emails will be sent.                                                  | `b0M0w@example.com`                   |

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