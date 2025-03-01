## 7.0.1 (2025-03-01)

### Fix

- **app**: re-add location fields to main agency level

## 7.0.0 (2025-03-01)

### BREAKING CHANGE

- `GET` `/data-sources`: `agencies` key for each data source now has `locations` field with list of locations, in place of flat locational data
  `GET``/data-sources/{id}`: `agencies` key for each data source now has `locations` field with list of locations, in place of flat locational data
  `GET``/data-sources/{id}/related-agencies`: All agencies now have `locations` field with list of locations, in place of flat locational data
  `GET` `/agencies`: All agencies now have `locations` field with list of locations, in place of flat locational data
  `GET` `/agencies/{id}`: Results now have `locations` field with list of locations, in place of flat locational data
  `PUT` `/agencies/{id}`: `location_id` field removed
  `POST` `/agencies`: `location_id` field replaced with `location_ids` field, which accepts list of integers representing location ids.
  `GET` `/match/agency`: Flat location keys removed and replaced with `locations` field with list of locations

### Feat

- **app**: allow agencies to have multiple locations

## 6.1.2 (2025-02-28)

### Fix

- **api**: refine `/archives` `PUT` limiter to 25/min, 1000/hour

## 6.1.1 (2025-02-28)

### Fix

- **database**: address comma in locality name

## 6.1.0 (2025-02-28)

### Feat

- **database**: add data_sources to change_log tracking

## 6.0.0 (2025-02-28)

### BREAKING CHANGE

- Batch update endpoints removed.

### Fix

- **api**: remove batch update endpoints

## 5.0.0 (2025-02-28)

### BREAKING CHANGE

- References to `submitted_name` in `data_sources` related endpoints have been removed -- only `name`, if anything, is included in their place.

### Fix

- **database**: remove select data sources columns

## 4.1.1 (2025-02-27)

### Fix

- **database**: remove column permission tables
- **database**: remove column permission tables

## 4.1.0 (2025-02-27)

### Feat

- **database**: rename select agency type values and set to enum in db

## 4.0.0 (2025-02-27)

### BREAKING CHANGE

- `approved` will no longer be a valid attribute on data sources to pull. Instead `approval_status` will need to be used.

### Fix

- **database**: remove agencies approved and add approval_status column

## 3.0.1 (2025-02-27)

### Fix

- **database**: remove name_ascii column from counties table

## 3.0.0 (2025-02-26)

### BREAKING CHANGE

- Prior means of refreshing sessions will not work -- the refresh token will have to be provided in the `authorization` header, and no access token should be provided
- Prior means of refreshing sessions will not work -- the refresh token will have to be provided in the `authorization` header, and no access token should be provided
- Prior means of refreshing sessions will not work -- the refresh token will have to be provided in the `authorization` header, and no access token should be provided
- `/agencies`, `/data-requests`, `POST` now no longer accept `location_info` inputs -- these have been replaced with `location_id`

### Feat

- **api**: add `/metadata/record-types-and-categories` endpoint
- **auth**: revamp `/refresh-session` endpoint
- **auth**: revamp `/refresh-session` endpoint
- **auth**: revamp `/refresh-session` endpoint
- **database**: add `archive_write` permission
- **api**: add `record_types` option to `/search/search-location-and-record-type`
- **ci/cd**: add auto-populate-pr github action
- **ci/cd**: add auto-populate-pr github action
- **ci/cd**: add auto-populate-pr github action
- **ci/cd**: add auto-populate-pr github action
- **ci/cd**: add auto-populate-pr github action
- **ci/cd**: add auto-populate-pr github action
- **ci/cd**: add auto-populate-pr github action
- **ci/cd**: add auto-populate-pr github action
- **ci/cd**: add auto-populate-pr github action
- **ci/cd**: add auto-populate-pr github action
- **ci/cd**: add auto-populate-pr github action
- **api**: add basic auth to `GET` `/locations/:id`
- **ci/cd**: add auto-populate-pr github action
- **database**: enhance typeahead_locations display_name
- **ci/cd**: add github caching
- **ci/cd**: add github caching
- **ci/cd**: add github caching
- **ci/cd**: add github caching
- **ci/cd**: add github caching
- **ci/cd**: add github caching
- **ci/cd**: add github caching
- **ci/cd**: add github caching
- **ci/cd**: add github caching
- **database**: add unique constraint for counties
- **database**: differentiate counties and county-level cities
- **database**: differentiate counties and county-level cities
- **database**: add `table_log` table
- **api**: update post endpoints with location_id
- **api**: remove homepage_search_cache endpoint and logic
- **api**: remove homepage_search_cache endpoint and logic
- **db_client**: add fuzzy matching backup to typeahead location
- **api**: add limit parameter to select endpoints
- **data_sources_app**: create `/contact/form-submit` endpoint
- **data_sources_app**: create `/contact/form-submit` endpoint
- **data_sources_app**: create `/contact/form-submit` endpoint

### Fix

- **ci/cd**: adjust logic for auto-populating dev->main pr
- **ci/cd**: attempt fix for pyproject
- **db_client**: fix bug in `get_metrics`
- **db_client**: add `unknown` agency_type
- **db_client**: fix bug in get_metrics()
- **data_sources_app**: remove semantic release and use commitizen only

### Refactor

- **resources**: rename GET_AUTH_INFO to API_OR_JWT_AUTH_INFO

## 2.0.0 (2025-02-11)

### Feat

- **data_sources_app**: Add Semantic Release Draft
- add v2 feature gating
- update profile
- add loader.io token
- **client**: data requests Add location requests to results, Add data-request/id route
- use new footer and donor box API
- updated authentication flow
- data source enhancements and follow searches (#199)
- use dark mode for inputs (#192)
- new data source route (#184)
- Github auth integration with client (#158)
- miscellaneous client search updates (#150)
- request route (#141)
- data source by id route (#122)
- **index.html**: replace franklin with public sans
- **pages**: build search results page
- beginnings of data source by id (#103)
- **components**: create password validator Abstract password validation UI into component Use component anywhere new passwords are created
- **search**: add main search route Add typeahead input Update index route
- add route transitions
- add file-based routing
- **config**: add logic to router to handle meta tags
- **pages**: add catchall 404 route
- **components**: Add error boundary
- **pages**: update DataSourceStaticView

### Fix

- profile loading
- search results lazy load
- search not displaying results on first query
- search results take 2
- search results
- client build
- nvmrc and update pack-lock
- location text
- get requests by location and miscellaneous other fixes
- location text formatting
- fetch all requests
- broken build
- miscellaneous client cleanup
- data requests get
- search with categories
- broken search form
- update location logic per API changes
- broken typeahead on request routes
- little problem with route getter
- miscellaneous results -> auth -> results fixes
- token validation granularity
- search results erroring
- search results error handling
- miscellaneous ds create fixes
- warning toast for existing url
- already exists logic
- add not found functionality to data source create
- data source id animation on swipe
- search
- reset password redirect (#176)
- trailing slash (#159)
- data source cleanup (#124)
- data source route prev/next (#123)
- search results follow-ups (#116)
- search form realignment (#114)
- search results alignment (#113)
- add password hinting to all routes
- not found text
- only search on 2 or more chars
- **tests**: update auth wrapper tests
- **pages**: Update ResetPassword Add password hints
- **pages**: update search results filtering Accommodate multiple items of each record_type
- miscellaneous styling issues
- **assets**: favicon not displaying
- **tests**: update tests for SearchResultsPage
- **tests**: update tests for SearchResultsCard
- use vite syntax for importing env vars (#169)
- quick-search (#138)
- client build (#131)

### Refactor

- miscellaneous client cleanup
- api, auth, client data caching (#218)
- move signup to auth, rename funcs
- use range date inputs and ds create cleanup (#201)
- clean up agencies UI and logic
- update password reset flow (#172)
- miscellaneous client organization (#170)
- airtable_uuid -> id (#135)
- `Form` -> `FormV2` and `PdapInput` -> v2 input components (#128)
- **components**: update search form Make viable for rendering in single column in search results
- **stores**: update source by id url
- use route tag to control auth routes
- updates to search and typeahead Make updates to smooth search experience
- update auth per new API strategy
- miscellaneous updates to router and app shell
- break meta functionality into separate funcs
- update auth strategy
- **test**: update testing Remove page-level tests, Re-introduce and refactor component and util tests
- **api**: Update quick_search_query.py function signatures
- **stores**: user Add func to check validity of reset token
- **pages**: ResetPassword Check token validity on page load
- **router**: miscellaneous updates
- **router**: organization and comments
- **router**: Update meta tag logic Add support for multiple matched routes
- **pages**: update search result page Handle UI more elegantly
- **pages**: update SearchResultPage Get count from API results Misc template cleanup
- **pages**: add error boundary to results render
- **components**: update error boundary add optional component prop
- **pages**: update login error handling
- **pages**: update password reset expired token UI
- **pages**: miscellaneous updates to search results page
- **components**: miscellaneous updates to search results card
- **util**: move page data and add search shape
- **util**: update formatDate to return undefined for invalid date passed
- update miscellaneous files with linting errors
- **util**: update formatDateForSearchResults
- remove coverage comment from links util
- move links to util
- remove unnecessary image asset
- update search more button (#181)
- data source static view (#173)
