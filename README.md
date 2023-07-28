# data-sources-app
An API and UI for using and maintaining the Data Sources database

## Installation

### 1. Clone this repository and navigate to the root directory.
```
git clone https://github.com/Police-Data-Accessibility-Project/data-sources-app.git
cd data-sources-app
```

### 2. Create an .env file in the root directory.
It should have a SUPABASE_URL and SUPABASE_KEY.

### 3. Create a virtual environment.
```
python3 -m venv venv
```

### 4. Activate the virtual environment.
```
source venv/bin/activate
```

### 5. Install dependencies.
```
pip install -r requirements.txt
```

### 6. Run the Python app.
```
python3 app.py
```

### 7. In a new terminal window, install the Vue app.
```
npm install
```

### 8. Run the development server.
```
cd client
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
