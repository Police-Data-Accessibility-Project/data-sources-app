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

Either add a `.env` file to your local root directory or manually export these secrets: `DO_DATABASE_URL` and `VITE_VUE_APP_BASE_URL`.  

Reach out to contact@pdap.io or make noise in Discord if you'd like access to these keys.

```
# .env

DO_DATABASE_URL="postgres://data_sources_app:<password>@db-postgresql-nyc3-38355-do-user-8463429-0.c.db.ondigitalocean.com:25060/defaultdb"
VITE_VUE_APP_BASE_URL="http://localhost:5000"
```

```
# shell

export DO_DATABASE_URL=postgres://data_sources_app:<password>@db-postgresql-nyc3-38355-do-user-8463429-0.c.db.ondigitalocean.com:25060/defaultdb
export VITE_VUE_APP_BASE_URL="http://localhost:5000"
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

All tests for the API live in the app_test.py file. It is best practice to add tests for any new feature to ensure it is working as expected and that any future code changes do not affect its functionality. All tests should be run before opening a PR (and when reviewing a PR) in order to ensure any changes do not break current app functionality. If a test fails, it is a sign that the new code should be checked or possibly that the test needs to be updated. Tests are currently run with pytest.

```
pip install pytest
pytest

```

## Other helpful commands for the client app

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

### Runs tests quietly
```
npm run test
```

### Runs tests and outputs coverage reports
```
npm run coverage
```

### Customize configuration

See [Configuration Reference](https://cli.vuejs.org/config/).
