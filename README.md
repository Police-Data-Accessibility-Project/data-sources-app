# data-sources-app

An API and UI for using and maintaining the Data Sources database. Documentation about how the app works can be found [here](https://docs.pdap.io/api/introduction).

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

virtualenv -p python3.9 venv

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

Either add a `.env` file to your local root directory or manually export these secrets: `DO_DATABASE_URL` and `VITE_VUE_API_BASE_URL`.  

Reach out to contact@pdap.io or make noise in Discord if you'd like access to these keys.

```
# .env

DO_DATABASE_URL="postgres://data_sources_app:<password>@db-postgresql-nyc3-38355-do-user-8463429-0.c.db.ondigitalocean.com:25060/defaultdb"
VITE_VUE_API_BASE_URL="http://localhost:5000"
VITE_VUE_APP_BASE_URL="http://localhost:8888"
```

```
# shell

export DO_DATABASE_URL=postgres://data_sources_app:<password>@db-postgresql-nyc3-38355-do-user-8463429-0.c.db.ondigitalocean.com:25060/defaultdb
export VITE_VUE_API_BASE_URL="http://localhost:5000"
export VITE_VUE_APP_BASE_URL="http://localhost:8888"
```

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

All unit tests for the API live in the app_test.py file. It is best practice to add tests for any new feature to ensure it is working as expected and that any future code changes do not affect its functionality. All tests will be automatically run when a PR into dev is opened in order to ensure any changes do not break current app functionality. If a test fails, it is a sign that the new code should be checked or possibly that the test needs to be updated. Tests are currently run with pytest and can be run locally with the `pytest` command.

Endpoints are structured for simplified testing and debugging. Code for interacting with the database is contained in a function suffixed with "_results" and tested against a local sqlite database instance. Limited rows (stored in the DATA_SOURCES_ROWS and AGENCIES_ROWS variables in app_test_data.py) are inserted into this local instance on setup, you may need to add additional rows to test other functionality fully. 

Remaining API code is stored in functions suffixed with "_query" tested against static query results stored in app_test_data.py. Tests for hitting the endpoint directly should be included in regular_api_checks.py, makes sure to add the test function name in the list at the bottom so it is included in the Github actions run every 15 minutes.

```
pip install pytest
pytest

```
## Linting
Linting is enforced with black on PR creation. You can use black to automatically reformat your files before commiting them, this will allow your PR to pass this check. Any files that require reformatting will be listed on any failed checks on the PR.
```
black app_test.py
```

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
