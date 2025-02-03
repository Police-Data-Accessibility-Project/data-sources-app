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

For more information on setting up environment secrets, see `ENV.md`

### 6. Set up Local Database

Follow instructions in the `/local_database` directory to set up a local database for testing.

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