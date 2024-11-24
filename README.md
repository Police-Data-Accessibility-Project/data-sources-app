![Python Version](https://img.shields.io/badge/python-3.12-blue?style=for-the-badge&logo=python&logoColor=ffdd54)

# data-sources-app-v2

Development of the next big iteration of the data sources app according to https://github.com/Police-Data-Accessibility-Project/data-sources-app/issues/248

An API and UI for searching, using, and maintaining Data Sources. 

#### [Live app](https://data-sources-v2.pdap.io/) deployed from `main`
#### [Dev app](https://data-sources-v2.pdap.dev/) deployed from `dev`
#### [API docs](https://docs.pdap.io/api/introduction)

## Installation

### 1. Clone this repository and navigate to the root directory.

```
git clone https://github.com/Police-Data-Accessibility-Project/data-sources-app.git
cd data-sources-app
```

### 2. Create a virtual environment.

If you don't already have virtualenv, install the package:

```

pip install virtualenv

```

Then run the following command to create a virtual environment:

```

virtualenv -p python3.11 venv

```

### 3. Activate the virtual environment.

```

source venv/bin/activate

```

### 4. Install dependencies.

```

pip install -r requirements.txt
pip install "psycopg[binary,pool]"

pre-commit install

# To optionally run the pre-commit against all files (as pre-commit usually only runs on changed files)
pre-commit run --all-files

```

### 5. Add environment secrets

In both the local root directory and the `/client` directory, either:
1. Either add a `.env` file to your local root directory with the below secrets
2. or manually export the below secrets

Reach out to contact@pdap.io or make noise in Discord if you'd like access to these keys.

The environment variables are as follows:
* DO_DATABASE_URL: Used to connect to the database.
* VITE_VUE_API_BASE_URL: The base URL for the API
* VITE_VUE_APP_BASE_URL: The base URL for the UI
* VITE_ADMIN_API_KEY: Used as the `Basic` auth token for the  web client. Must be in `/client` directory `.env` file.
* GH_CLIENT_ID: Used to authenticate with GitHub via OAuth. Must correspond to the `client_id` provided by GitHub.
* GH_CLIENT_SECRET: Used to authenticate with GitHub via OAuth. Must correspond to the `client_secret` provided by GitHub.
* JWT_SECRET_KEY: Used to sign and verify JWT tokens. Used to identify that any JWT tokens produced are recognizable by this version of the app and no other. Can be customized for local development.
* RESET_PASSWORD_SECRET_KEY: Used to sign and verify JWT tokens for the reset password feature. Used to identify that any JWT tokens for the reset password feature produced are recognizable by this version of the app and no other.
* FLASK_APP_COOKIE_ENCRYPTION_KEY: Used to create signed cookies to prevent CSRF attacks. Used to identify that any cookies produced are recognizable by this version of the app and no other. Can be customized for local development.
* DEVELOPMENT_PASSWORD: Used to create a test user with elevated permissions for the purposes of testing. Developers must provide this password when using the `/dev/create-test-user-with-elevated-permissions` endpoint. Can be customized for local development.
* GH_API_ACCESS_TOKEN: Used to authenticate with GitHub when adding or getting information about Github Issues. Must correspond to the `access_token` provided by GitHub.
* GH_ISSUE_REPO_NAME: Identifies the repository, in `<github-username>/<github-repo-name>` format, where the issue will be created, and where information about issues will be retrieved. Can be customized for local development.
* VALIDATE_EMAIL_SECRET_KEY: Used to sign and verify JWT tokens for the validate email feature. Used to identify that any JWT tokens for the validate email feature produced are recognizable by this version of the app and no other.


#### .env Example
```
# .env

DO_DATABASE_URL="postgres://data_sources_app:<password>@db-postgresql-nyc3-38355-do-user-8463429-0.c.db.ondigitalocean.com:25060/defaultdb"
VITE_VUE_API_BASE_URL="http://localhost:5000"
VITE_VUE_APP_BASE_URL="http://localhost:8888"
VITE_ADMIN_API_KEY="1234abcd"
GH_CLIENT_ID="GithubProvidedClientId"
GH_CLIENT_SECRET="GithubProvidedClientSecret"
FLASK_APP_COOKIE_ENCRYPTION_KEY="myCustomFlaskAppSecretKey"
JWT_SECRET_KEY="myCustomJwtSecretKey"
RESET_PASSWORD_SECRET_KEY="myCustomResetPasswordSecretKey"
DEVELOPMENT_PASSWORD="myCustomDevelopmentPassword"
GH_API_ACCESS_TOKEN="GithubProvidedAccessToken"
GH_ISSUE_REPO_NAME="github-username/github-repo-name"
VALIDATE_EMAIL_SECRET_KEY="myCustomValidateEmailSecretKey"
```

#### Shell Example
```shell
# shell

export DO_DATABASE_URL=postgres://data_sources_app:<password>@db-postgresql-nyc3-38355-do-user-8463429-0.c.db.ondigitalocean.com:25060/defaultdb
# etc.
```
Additionally, if you are testing the email functionality, you will need to also provide the `MAILGUN_KEY` environment variable as well (also obtainable from the sources mentioned above).


### 6. Allow your IP address

To connect to the database, your IP address will need to be added to the "allow" list in DigitalOcean database settings. Reach out to someone with admin access to get your IP address added.

### 7. Run the Python app.

```

python3 app.py

```


### 8. In a new terminal window, install the Vue app.

```

cd client
npm install

```

### 9. Run the development server.

```

npm run dev

```

## Contributing
If you're here to submit a Pull Request, please review the important information available in CONTRIBUTING.md.