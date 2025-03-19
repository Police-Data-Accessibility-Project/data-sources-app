![Python Version](https://img.shields.io/badge/python-3.12-blue?style=for-the-badge&logo=python&logoColor=ffdd54)

# data-sources-app

An API for searching, using, and maintaining Data Sources. 

#### Live app: https://data-sources.pdap.io/ deployed from `main`
#### Dev app:https://data-sources.pdap.dev/ deployed from `dev`
#### API docs / base URL: https://data-sources.pdap.io/api (or ...dev/api)

## Running the app for local development

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

For more information on setting up environment secrets, see `ENV.md`

### 6. Set up Local Database

Follow instructions in the `/local_database` directory to set up a local database for testing.

### 7. Run the Python app.

```

python3 app.py

```


### 8. (If necessary) run the client locally against the API

If you need to run the client web application, refer to the [pdap.io documentation](https://github.com/Police-Data-Accessibility-Project/pdap.io). 

Generally, local development on the client is done based on the stable deployed `dev` API, and API development can usually be verified using `curl`. But if you are working on a full stack project for which you need to run the client locally against the API locally, reach out to @maxachis and @joshuagraber in Discord for help.

## Contributing
If you're here to submit a Pull Request, please review the important information available in CONTRIBUTING.md.
