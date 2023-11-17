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

### 5. Manually export a DO_DATABASE_URL, SECRET_KEY, and WEBHOOK_URL in the command line

The app should have a DO_DATABASE_URL, SECRET_KEY, and WEBHOOK_URL for PDAP's Data Sources [Supabase](https://supabase.com/). Reach out to contact@pdap.io or make noise in Discord if you'd like access to these keys.

```
export DO_DATABASE_URL=postgres://data_sources_app:<password>@db-postgresql-nyc3-38355-do-user-8463429-0.c.db.ondigitalocean.com:25060/defaultdb
export SECRET_KEY=<secret_key>
export WEBHOOK_URL=<webhook_url>

```

### 6. Run the Python app.

```

python3 app.py

```

### 7. In a new terminal window, install the Vue app.

```

cd client
npm install

```

### 8. Run the development server.

```

npm run serve

```

## Other helpful commands

### Compiles and minifies for production

```

npm run build

```

### Lints and fixes files

```

npm run lint

```

### Customize configuration

See [Configuration Reference](https://cli.vuejs.org/config/).

```

```
