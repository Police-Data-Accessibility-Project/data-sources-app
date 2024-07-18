![Python Version](https://img.shields.io/badge/python-3.11-blue?style=for-the-badge&logo=python&logoColor=ffdd54)

# data-sources-app-v2

Development of the next big iteration of the data sources app according to https://github.com/Police-Data-Accessibility-Project/data-sources-app/issues/248

An API and UI for searching, using, and maintaining Data Sources. 

#### [Live app](https://data-sources.pdap.io/)
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

```

### 5. Add environment secrets

In both the local root directory and the `/client` directory, either:
1. Either add a `.env` file to your local root directory with the below secrets
2. or manually export the below secrets

Reach out to contact@pdap.io or make noise in Discord if you'd like access to these keys.

```
# .env

DO_DATABASE_URL="postgres://data_sources_app:<password>@db-postgresql-nyc3-38355-do-user-8463429-0.c.db.ondigitalocean.com:25060/defaultdb"
DEV_DB_CONN_STRING="postgresql://data_sources_app_v2:<password>@pdap-db-dev-do-user-8463429-0.c.db.ondigitalocean.com:25060/pdap_dev_db?sslmode=require"
VITE_VUE_API_BASE_URL="http://localhost:5000"
VITE_VUE_APP_BASE_URL="http://localhost:8888"
SECRET_KEY="mySecretKey"
```

```
# shell

export DO_DATABASE_URL=postgres://data_sources_app:<password>@db-postgresql-nyc3-38355-do-user-8463429-0.c.db.ondigitalocean.com:25060/defaultdb
export DEV_DB_CONN_STRING="postgresql://data_sources_app_v2:<password>@pdap-db-dev-do-user-8463429-0.c.db.ondigitalocean.com:25060/pdap_dev_db?sslmode=require"
export VITE_VUE_API_BASE_URL="http://localhost:5000"
export VITE_VUE_APP_BASE_URL="http://localhost:8888"
export SECRET_KEY="mySecretKey"
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

## Testing

### Location
All unit and integration tests for the API live in the `tests` folder

It is best practice to add tests for any new feature to ensure it is working as expected and that any future code changes do not affect its functionality. All tests will be automatically run when a PR into dev is opened in order to ensure any changes do not break current app functionality. If a test fails, it is a sign that the new code should be checked or possibly that the test needs to be updated. 


### How to run tests
Some tests involve interfacing with the development database, which copies the production database's data and schema daily.

To ensure such tests properly connect to the database, create or amend an `.env` file in the root direct of the project with the environment variable `DEV_DB_CONN_STRING`. Provide as a value a connection string giving you access to the `data_sources_app` user. If you do not have this connection string, DM a database administrator.

Tests are currently run with pytest and can be run locally with the `pytest` command.

Remaining API code is stored in functions suffixed with "_query" tested against static query results stored in app_test_data.py.

```
pip install pytest
pytest

```
## Linting
Linting is enforced with black on PR creation. You can use black to automatically reformat your files before commiting them, this will allow your PR to pass this check. Any files that require reformatting will be listed on any failed checks on the PR.
```
black app_test.py
```

## Docstring and Type Checking

Docstrings and Type Checking are checked using the [pydocstyle](https://www.pydocstyle.org/en/stable/) and [mypy](https://mypy-lang.org/)
modules, respectively. When making a pull request, a Github Action (`python_checks.yml`) will run and, 
if it detects any missing docstrings or type hints in files that you have modified, post them in the Pull Request.

These will *not* block any Pull request, but exist primarily as advisory comments to encourage good coding standards.

Note that `python_checks.yml` will only function on pull requests made from within the repo, not from a forked repo.

## Client App

A few things to know:

- We use Vue3. This allows for using either the options or composition APIs. Feel free to use whichever you are most fluent in.
- We use `pinia` for state management. This works much better with the composition API than with options, so it is recommended to use the composition API if you need data from one of the `pinia` stores.

### Compiles and minifies for production
```
npm run build
```

### Serves production build locally
```
npm run preview
```

### Lints files
```
npm run lint
```

### Lints and fixes any fixable errors
```
npm run lint:fix
```

### Runs tests with debug output
```
npm run test
```

### Runs tests quietly for CI
```
npm run test:ci
```

### Runs tests only on changed files
```
npm run test:changed
```

### Runs tests and outputs coverage reports
```
npm run coverage
```

### Customize configuration

See [Configuration Reference](https://cli.vuejs.org/config/).
