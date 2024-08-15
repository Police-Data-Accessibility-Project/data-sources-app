![Python Version](https://img.shields.io/badge/python-3.11-blue?style=for-the-badge&logo=python&logoColor=ffdd54)

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

```

### 5. Add environment secrets

In both the local root directory and the `/client` directory, either:
1. Either add a `.env` file to your local root directory with the below secrets
2. or manually export the below secrets

Reach out to contact@pdap.io or make noise in Discord if you'd like access to these keys.

The environment variables are as follows:
* DO_DATABASE_URL: Used to connect to the database
* DEV_DB_CONN_STRING: Used to connect to the dev database
* VITE_VUE_API_BASE_URL: The base URL for the API
* VITE_VUE_APP_BASE_URL: The base URL for the UI
* JWT_SECRET_KEY: Used to sign and verify JWT tokens
* FLASK_APP_SECRET_KEY: Used to create signed cookies to prevent CSRF attacks
* GH_CLIENT_ID: Used to authenticate with GitHub via OAuth
* GH_CLIENT_SECRET: Used to authenticate with GitHub via OAuth

#### .env Example
```
# .env

DO_DATABASE_URL="postgres://data_sources_app:<password>@db-postgresql-nyc3-38355-do-user-8463429-0.c.db.ondigitalocean.com:25060/defaultdb"
DEV_DB_CONN_STRING="postgresql://data_sources_app_v2:<password>@pdap-db-dev-do-user-8463429-0.c.db.ondigitalocean.com:25060/pdap_dev_db?sslmode=require"
VITE_VUE_API_BASE_URL="http://localhost:5000"
VITE_VUE_APP_BASE_URL="http://localhost:8888"
FLASK_APP_SECRET_KEY="myFlaskAppSecretKey"
JWT_SECRET_KEY="myJwtSecretKey"
GH_CLIENT_ID="myGithubClientId"
GH_CLIENT_SECRET="myGithubClientSecret"
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