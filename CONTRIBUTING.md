# Contributing

This guide contains information which will help you submit code to the Data Sources App.

## Installation
Follow instructions in README.md.

## Testing

### Location
All unit and integration tests for the API live in the `tests` folder

It is best practice to add tests for any new feature to ensure it is working as expected and that any future code changes do not affect its functionality. All tests will be automatically run when a PR into dev is opened in order to ensure any changes do not break current app functionality. If a test fails, it is a sign that the new code should be checked or possibly that the test needs to be updated. 

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

### Test Databases

Currently, two test databases exist:

* Sandbox - This is to be used by developers to test out changes to the schema and content of the database in connection with development versions of the app. Sensitive information from the production database, such as user information, are excluded in this environment.
* Stage - This is used to test stage code in an environment as closely modeling the production database as possible, and is not designed to be accessed directly by developers. Sensitive information is included in this environment.

Both databases are refreshed daily from the production database, using logic in the [https://github.com/Police-Data-Accessibility-Project/prod-to-dev-migration](https://github.com/Police-Data-Accessibility-Project/prod-to-dev-migration) repository. Additionally, they are updated with SQL code from [dev\_scripts.sql](https://github.com/Police-Data-Accessibility-Project/prod-to-dev-migration/blob/main/dev\_scripts.sql), which provides the most up-to-date development version of the database.

### Obtaining test database information for admins

Connection information can be obtained through access the databases on Digital Ocean.

* In [https://cloud.digitalocean.com/databases](https://cloud.digitalocean.com/databases?i=feca0b), you will be able to select different databases. From here, you can click on the `Actions` dropdown, and select `Connection Details` to obtain information about the relevant connection.

Login information for users can be obtained through environment variables provided for the Prod to Stage and Sandbox Migration Job, currently located at: [https://automation.pdap.io/job/Prod%20to%20Stage%20and%20Sandbox%20Migration/configure](https://automation.pdap.io/job/Prod%20to%20Stage%20and%20Sandbox%20Migration/configure)

* Look for environment variables for:
  * SANDBOX\_DEV\_USER
  * SANDBOX\_DEV\_PASSWORD
* Additional information about the database, including the server name, the port number, and the database name, can also be found on connection strings labeled with the "SANDBOX\_" or "STAGE\_" prefixes.



### Running Tests Locally

A connection string will need to be input into the `DEV_DB_CONN_STRING` and `DO_DATABASE_URL` environment variables for your local copy of [data\_sources\_app ](https://github.com/Police-Data-Accessibility-Project/data-sources-app). This connection string will take the following form:

`postgresql://user:password@server:port/dbname?sslmod=require`

Once this is set, you can run tests by running `pytest <directory-or-file>`

Full pytest documentation can be found [here](https://docs.pytest.org/en/stable/contents.html).


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

