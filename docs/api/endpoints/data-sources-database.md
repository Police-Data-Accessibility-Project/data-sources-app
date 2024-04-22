---
description: Use the API to find, use, and manage Data Sources.
---

# Data Sources database

## Base URL

```
https://data-sources.pdap.io
```

## Search Tokens

## Generate API token for front end search

<mark style="color:blue;">`GET`</mark> `[base-url]/search-tokens`

The search tokens endpoint is located in [resources/SearchTokens.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/QuickSearch.py). The search tokens endpoint generates an API token valid for 5 minutes and forwards the search parameters to the Quick Search endpoint. This endpoint is meant for use by the front end only.

#### Query Parameters

| Name                                   | Type   | Description                                                                                                                                   |
| -------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| arg1<mark style="color:red;">\*</mark> | String | The first argument that will be forwarded on to the appropriate endpoint. Currently either "search" for quick-search or "id" for data-sources |
| arg2<mark style="color:red;">\*</mark> | String | The second argument that will be forwarded on to the appropriate endpoint. Currently just used for "location" for quick-search                |
| endpoint                               | String | The endpoint that will be accessed after a search token is generated                                                                          |

{% tabs %}
{% tab title="200: OK Successful operation" %}
{% tabs %}
{% tab title="Schema" %}
<pre class="language-plsql"><code class="lang-plsql">count int
<strong>data array[object]
</strong>    agency_name string
    municipality string
    state_iso string
    data_source_name string
    description string
    record_type string
    source_url string
    record_format string
    coverage_start string
    coverage_end string
    agency_supplied boolean
</code></pre>
{% endtab %}

{% tab title="Example" %}
```json
{
	"count": 1,
	"data": [
		{
			"agency_name": "Allegheny County Police Department - PA",
			"municipality": "Pittsburgh",
			"state_iso": "PA",
			"data_source_name": "Allegheny County Police Review Board Transcripts",
			"description": null,
			"record_type": "Policies & Contracts",
			"source_url": "https://www.alleghenycounty.us/county-council/police-review-board-meetings.aspx",
			"record_format": "[\"PDF: Machine Created\"]",
			"coverage_start": "2018-08-29",
			"coverage_end": "2018-09-26",
			"agency_supplied": true
		}
	]
}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="500: Internal Server Error Error" %}
```javascript
{
    "message": error
}
```
{% endtab %}
{% endtabs %}

## Search

## Quick Search Data Sources by search term and location

<mark style="color:blue;">`GET`</mark> `[base-url]/quick-search/{search}/{location}`

The quick search endpoint is located in [resources/QuickSearch.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/QuickSearch.py). The quick search endpoint executes its search using the agency\_source\_link table in the Data Sources database, which links each data source in the data\_sources table with its associated agency in the agencies table. This endpoint is meant for use by the search tokens endpoint only.

#### Path Parameters

| Name                                       | Type   | Description                                                                                                                                                                                                                                   |
| ------------------------------------------ | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| search<mark style="color:red;">\*</mark>   | String | Checks partial matches on any of the following properties on the data\_source table: "name", "description", "record\_type", and "tags". The search term will is case insensitive and will match singular and pluralized versions of the term. |
| location<mark style="color:red;">\*</mark> | String | Checks partial matches on any of the following properties on the agencies table: "county\_name", "state\_iso", "municipality", "agency\_type", "jurisdiction\_type", "name"                                                                   |

#### Headers

| Name                                            | Type   | Description                                         |
| ----------------------------------------------- | ------ | --------------------------------------------------- |
| Authorization<mark style="color:red;">\*</mark> | String | Value formatted as "Bearer \[access token/api key]” |

{% tabs %}
{% tab title="200: OK Successful operation" %}
{% tabs %}
{% tab title="Schema" %}
<pre class="language-plsql"><code class="lang-plsql">count int
<strong>data array[object]
</strong>    agency_name string
    municipality string
    state_iso string
    data_source_name string
    description string
    record_type string
    source_url string
    record_format string
    coverage_start string
    coverage_end string
    agency_supplied boolean
</code></pre>
{% endtab %}

{% tab title="Example" %}
```json
{
	"count": 1,
	"data": [
		{
			"agency_name": "Allegheny County Police Department - PA",
			"municipality": "Pittsburgh",
			"state_iso": "PA",
			"data_source_name": "Allegheny County Police Review Board Transcripts",
			"description": null,
			"record_type": "Policies & Contracts",
			"source_url": "https://www.alleghenycounty.us/county-council/police-review-board-meetings.aspx",
			"record_format": "[\"PDF: Machine Created\"]",
			"coverage_start": "2018-08-29",
			"coverage_end": "2018-09-26",
			"agency_supplied": true
		}
	]
}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="403: Forbidden Invalid API key" %}

{% endtab %}

{% tab title="500: Internal Server Error Something went wrong" %}
```
{
	"count": 0,
	"message": error
}
```
{% endtab %}

{% tab title="400: Bad Request Missing or bad API key" %}
```javascript
{
    // Response
}
```
{% endtab %}
{% endtabs %}

## Data Sources

## Get all Data Sources

<mark style="color:blue;">`GET`</mark> `[base-url]/data-sources`

The data sources endpoint is located in [resources/DataSources.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/QuickSearch.py). The data sources endpoint returns all approved rows in the corresponding Data Sources database table by default. An optional JSON object can be passed to get data sources needing identification instead.

#### Headers

| Name                                            | Type   | Description                                         |
| ----------------------------------------------- | ------ | --------------------------------------------------- |
| Authorization<mark style="color:red;">\*</mark> | String | Value formatted as "Bearer \[access token/api key]” |

#### Request Body

| Name | Type | Description                                                              |
| ---- | ---- | ------------------------------------------------------------------------ |
| Data | JSON | In order to get data sources needing identification: {"approved": False} |

{% tabs %}
{% tab title="200: OK Successful operation" %}
{% tabs %}
{% tab title="Schema" %}
<pre class="language-plsql"><code class="lang-plsql">count int
<strong>data array[object]
</strong>    name string
    submitted_name string
    description string
    record_type string
    source_url string
    agency_supplied boolean
    supplying_entity string
    agency_originated string
    originating_entity string
    agency_aggregation string
    coverage_start string
    coverage_end string
    source_last_updated string
    retention_schedule string
    detail_level string
    number_of_records_available string
    size string
    access_type array
    data_portal_type string
    record_format array
    update_frequency string
    update_method string
    tags string
    readme_url string
    scraper_url string
    data_source_created string
    airtable_source_last_modified string
    url_status string
    rejection_note string
    last_approval_editor object
    agency_described_submitted string
    agency_described_not_in_database string
    approval_status string
    record_type_other string
    data_portal_type_other string
    records_not_online string
    data_source_request string
    url_button string
    tags_other string
    access_notes string
    last_cached string
</code></pre>
{% endtab %}

{% tab title="Example" %}
<pre class="language-json"><code class="lang-json">count: 1
<strong>[{'name': 'Calls for Service for Chicago Police Department - IL', 'submitted_name': None, 'description': None, 'record_type': 'Calls for Service', 'source_url': 'https://informationportal.igchicago.org/911-calls-for-cpd-service/', 'agency_supplied': True, 'supplying_entity': None, 'agency_originated': None, 'originating_entity': None, 'agency_aggregation': None, 'coverage_start': '2019-01-01', 'coverage_end': None, 'source_last_updated': None, 'retention_schedule': None, 'detail_level': 'Summarized totals', 'number_of_records_available': None, 'size': None, 'access_type': ['Web page'], 'data_portal_type': None, 'record_format': None, 'update_frequency': 'Bi-weekly', 'update_method': None, 'tags': None, 'readme_url': None, 'scraper_url': None, 'data_source_created': '2022-09-28', 'airtable_source_last_modified': '2023-11-08', 'url_status': 'ok', 'rejection_note': None, 'last_approval_editor': '{"id": "usrtLIB4Vr3jTH8Ro", "email": "josh.chamberlain@pdap.io", "name": "Josh Chamberlain"}', 'agency_described_submitted': 'Chicago city, Illinois', 'agency_described_not_in_database': None, 'approval_status': 'approved', 'record_type_other': None, 'data_portal_type_other': None, 'records_not_online': None, 'data_source_request': None, 'url_button': None, 'tags_other': None, 'access_notes': None, 'last_cached': '2024-01-30', 'agency_name': 'Chicago Police Department - IL'}]
</strong></code></pre>
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="400: Bad Request Missing or bad API key" %}
```javascript
{
    // Response
}
```
{% endtab %}

{% tab title="403: Forbidden Invalid API key" %}

{% endtab %}

{% tab title="500: Internal Server Error Error" %}
```javascript
{
	"count": 0,
	"message": "There has been an error pulling data!"
}
```
{% endtab %}
{% endtabs %}

## Data Sources for Map

<mark style="color:blue;">`GET`</mark> `[base-url]/data-sources-map`

#### Headers

The data sources for map endpoint is located in [resources/DataSourcesMap.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/DataSourcesMap.py). The data sources endpoint returns all approved rows in the corresponding Data Sources database table by default with only the columns relevant to mapping.

| Name                                            | Type   | Description                                         |
| ----------------------------------------------- | ------ | --------------------------------------------------- |
| Authorization<mark style="color:red;">\*</mark> | String | Value formatted as "Bearer \[access token/api key]” |

{% tabs %}
{% tab title="200: OK Successful operation" %}
{% tabs %}
{% tab title="Schema" %}
<pre class="language-plsql"><code class="lang-plsql">count int
<strong>data array[object]
</strong>    data_source_id string
    name string
    agency_id string
    agency_name string
    state_iso string
    municipality string
    county_name array[string]
    record_type string
    lat float
    lng float
</code></pre>
{% endtab %}

{% tab title="Example" %}
<pre class="language-json"><code class="lang-json">count: 1
<strong>[{'data_source_id': 'recisSIaKGoWWbC8y', 'name': 'Allegheny County Jail policies', 'agency_id': 'recNjgPW5kD573LeK', 'agency_name': 'Allegheny County Jail', 'state_iso': 'PA', 'municipality': None, 'county_name': '["Allegheny"]', 'record_type': 'Policies &#x26; Contracts', 'lat': 40.4345561, 'lng': -79.9959509}]
</strong></code></pre>
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="400: Bad Request Missing or bad API key" %}
```javascript
{
    // Response
}
```
{% endtab %}

{% tab title="403: Forbidden Invalid API key" %}

{% endtab %}

{% tab title="500: Internal Server Error Error" %}
```javascript
{
	"count": 0,
	"message": "There has been an error pulling data!"
}
```
{% endtab %}
{% endtabs %}

## Get Data Source by Id

<mark style="color:blue;">`GET`</mark> `[base-url]/data-sources-by-id/[id]`

The data sources endpoint is located in [resources/DataSources.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/QuickSearch.py). The data source by id endpoint returns just the row for the data source that corresponds to the id passed.

#### Path Parameters

| Name                                 | Type   | Description    |
| ------------------------------------ | ------ | -------------- |
| id<mark style="color:red;">\*</mark> | String | Data source id |

#### Headers

| Name                                            | Type   | Description                                         |
| ----------------------------------------------- | ------ | --------------------------------------------------- |
| Authorization<mark style="color:red;">\*</mark> | String | Value formatted as "Bearer \[access token/api key]” |

{% tabs %}
{% tab title="200: OK Successful operation" %}
{% tabs %}
{% tab title="Schema" %}
```plsql
count int
data array[object]
    name string
    submitted_name string
    description string
    record_type string
    source_url string
    agency_supplied boolean
    supplying_entity string
    agency_originated string
    originating_entity string
    agency_aggregation string
    coverage_start string
    coverage_end string
    source_last_updated string
    retention_schedule string
    detail_level string
    number_of_records_available string
    size string
    access_type array
    data_portal_type string
    record_format array
    update_frequency string
    update_method string
    tags string
    readme_url string
    scraper_url string
    data_source_created string
    airtable_source_last_modified string
    url_status string
    rejection_note string
    last_approval_editor object
    agency_described_submitted string
    agency_described_not_in_database string
    approval_status string
    record_type_other string
    data_portal_type_other string
    records_not_online string
    data_source_request string
    url_button string
    tags_other string
    access_notes string
    last_cached string
    homepage_url string
    count_data_sources string
    agency_type string
    multi_agency string
    submitted_name string
    jurisdiction_type string
    state_iso string
    municipality string
    zip_code string
    county_fips string
    county_name array
    lat float
    lng float
    data_sources array
    no_web_presence string
    airtable_agency_last_modified string
    data_sources_last_updated string
    approved boolean
    rejection_reason string
    last_approval_editor object
    agency_created string
    county_airtable_uid string
    defunct_year string
    data_source_id string
    agency_id string
    agency_name string
```
{% endtab %}

{% tab title="Example" %}
```json
{
    "data": {'name': 'Calls for Service for Asheville Police Department - NC', 'submitted_name': 'Asheville Police Department', 'description': None, 'record_type': 'Calls for Service', 'source_url': 'https://services.arcgis.com/aJ16ENn1AaqdFlqx/arcgis/rest/services/APD_CAD_911_Calls_2006/FeatureServer/0', 'agency_supplied': True, 'supplying_entity': None, 'agency_originated': None, 'originating_entity': None, 'agency_aggregation': None, 'coverage_start': '2006-01-01', 'coverage_end': '2006-12-31', 'source_last_updated': None, 'retention_schedule': None, 'detail_level': None, 'number_of_records_available': None, 'size': None, 'access_type': ['API', 'Download'], 'data_portal_type': 'ArcGIS', 'record_format': ['GIS / Shapefile'], 'update_frequency': None, 'update_method': None, 'tags': None, 'readme_url': 'https://docs.google.com/document/d/143a0LoGwNwmmHxJu1msxjOFAfAXPk7otQSWkrLtUDk0/edit?usp=sharing', 'scraper_url': 'https://pypi.org/project/openpolicedata/', 'data_source_created': '2023-03-02', 'airtable_source_last_modified': '2023-11-08', 'url_status': 'ok', 'rejection_note': None, 'last_approval_editor': '{"id": "usrtLIB4Vr3jTH8Ro", "email": "josh.chamberlain@pdap.io", "name": "Josh Chamberlain"}', 'agency_described_submitted': None, 'agency_described_not_in_database': None, 'approval_status': 'approved', 'record_type_other': None, 'data_portal_type_other': None, 'records_not_online': None, 'data_source_request': None, 'url_button': None, 'tags_other': None, 'access_notes': None, 'last_cached': '0001-01-01', 'homepage_url': 'https://www.ashevillenc.gov/department/police', 'count_data_sources': 18, 'agency_type': 'law enforcement/police', 'multi_agency': None, 'jurisdiction_type': 'local', 'state_iso': 'NC', 'municipality': 'Asheville', 'zip_code': '28801', 'county_fips': '37021', 'county_name': ['Buncombe'], 'lat': 35.594677, 'lng': -82.54986, 'data_sources': ['recpWxJ9JVa6BtLi5', 'reczwxaH31Wf9gRjS', 'recBd7NrWsvfTyDk0', 'recy24QB6I8FCVrQr', 'recW6aQGuNyzedIDl', 'recmrXPvQn9Gtfpba', 'recsojoTxJ3g08qKl', 'recTUW1QUZpsGVxoJ', 'reckqhpMEvDgiDGXF', 'recjnLeosesVTaW2r', 'reccrwbvTL6Ttd8XT', 'reckiy2nuY5iRptBm', 'recyJMD6eYF9Ln98B', 'recLdzmQMXC3XuPWU', 'recRNvjKBo5LkUBS9', 'recKFoiPMOmWFZvqM', 'recordd7DcM3raQF7', 'recV35fyFlof4pQXP'], 'no_web_presence': None, 'airtable_agency_last_modified': '2023-05-16', 'data_sources_last_updated': '2023-03-02', 'approved': True, 'rejection_reason': None, 'agency_created': '2022-08-18', 'county_airtable_uid': 'recrCy8hHYuxC8ZhU', 'defunct_year': None, 'data_source_id': 'reczwxaH31Wf9gRjS', 'agency_id': 'recJDGmbd7UMFcfa0', 'agency_name': 'Asheville Police Department - NC'}
}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="400: Bad Request Missing or bad API key" %}
{% tabs %}
{% tab title="Schema" %}
```plsql
count int
data array[object]
```
{% endtab %}

{% tab title="Example" %}
```json
{
	"count": 0,
	"data": []
}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="403: Forbidden Invalid API key" %}

{% endtab %}

{% tab title="500: Internal Server Error Error" %}
```javascript
{
	"message": "There has been an error pulling data!"
}
```
{% endtab %}

{% tab title="404: Not Found Id not found" %}
```javascript
{
    "message": "Data source not found."
}
```
{% endtab %}
{% endtabs %}

## Create Data Source

<mark style="color:green;">`POST`</mark> `[base-url]/data-sources`

The data sources endpoint is located in [resources/DataSources.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/QuickSearch.py). The create data source endpoint posts a new data source to the database and returns True if successful and False if not.

#### Headers

| Name                                            | Type   | Description                                         |
| ----------------------------------------------- | ------ | --------------------------------------------------- |
| Authorization<mark style="color:red;">\*</mark> | String | Value formatted as "Bearer \[access token/api key]” |

#### Request Body

| Name | Type | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ---- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Data | JSON | <p>A JSON object of the data source information. Refer to the Data Source dictionary for available fields: <a href="https://docs.pdap.io/activities/data-dictionaries/data-sources-data-dictionary">https://docs.pdap.io/activities/data-dictionaries/data-sources-data-dictionary</a>. However, the following fields cannot be edited: rejection_note, data_source_request, approval_status, airtable_uid, airtable_source_last_modified </p><p></p><p>Below is an example of an acceptable body:</p><p>{ "name":  "Calls for Service for Chicago Police Department - IL",</p><p>"record_type": "Calls for Service",</p><p>"source_url": "https://informationportal.igchicago.org/911-calls-for-cpd-service",</p><p>"coverage_start": "2019-01-01"</p><p>}</p> |

{% tabs %}
{% tab title="200: OK Successful operation" %}
{% tabs %}
{% tab title="Schema" %}
```plsql
message string
```
{% endtab %}

{% tab title="Example" %}
```json
{"message": "Data source added successfully."}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="403: Forbidden Invalid API key" %}

{% endtab %}

{% tab title="500: Internal Server Error Error" %}
```javascript
{
    "message": "There has been an error adding the data source"
}
```
{% endtab %}

{% tab title="400: Bad Request Missing or bad API key" %}
```javascript
{
    // Response
}
```
{% endtab %}
{% endtabs %}

## Update Data Source by Id

<mark style="color:orange;">`PUT`</mark> `[base-url]/data-sources-by-id/[id]`

The data sources endpoint is located in [resources/DataSources.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/QuickSearch.py). The update data source by id endpoint updates a data source and returns a status to confirm a successful update.

#### Path Parameters

| Name                                 | Type   | Description    |
| ------------------------------------ | ------ | -------------- |
| id<mark style="color:red;">\*</mark> | String | Data source id |

#### Headers

| Name                                            | Type   | Description                                         |
| ----------------------------------------------- | ------ | --------------------------------------------------- |
| Authorization<mark style="color:red;">\*</mark> | String | Value formatted as "Bearer \[access token/api key]” |

#### Request Body

| Name | Type | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ---- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Data | JSON | <p>A JSON object of the data to be updated. Refer to the Data Source dictionary for available fields: <a href="https://docs.pdap.io/activities/data-dictionaries/data-sources-data-dictionary">https://docs.pdap.io/activities/data-dictionaries/data-sources-data-dictionary</a>. However, the following fields cannot be edited: data_source_request, airtable_uid, airtable_source_last_modified</p><p></p><p>Below is an example of an acceptable body:</p><p>{ "name":  "Calls for Service for Chicago Police Department - IL",</p><p>"record_type": "Calls for Service",</p><p>"source_url": "https://informationportal.igchicago.org/911-calls-for-cpd-service",</p><p>"coverage_start": "2019-01-01"</p><p>}</p> |

{% tabs %}
{% tab title="200: OK Successful operation" %}
```json
{"message": "Data source successfully updated."}
```
{% endtab %}

{% tab title="500: Internal Server Error Error" %}
```javascript
{
    "message": "There has been an error updating the data source"
}
```
{% endtab %}

{% tab title="403: Forbidden Invalid API key" %}
```javascript
{
    // Response
}
```
{% endtab %}

{% tab title="400: Bad Request Missing or bad API key" %}
```javascript
{
    // Response
}
```
{% endtab %}
{% endtabs %}

## Archives

## Get all Archived urls

<mark style="color:blue;">`GET`</mark> `[base-url]/archives`

The archives endpoint is located in [resources/Archives.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/Archives.py). The get method  on the archives endpoint returns all rows for urls that the [automatic archives](https://github.com/Police-Data-Accessibility-Project/automatic-archives/blob/main/cache\_url.py) script has cached in the Internet Archive.

#### Headers

| Name                                            | Type   | Description                                         |
| ----------------------------------------------- | ------ | --------------------------------------------------- |
| Authorization<mark style="color:red;">\*</mark> | String | Value formatted as "Bearer \[access token/api key]” |

{% tabs %}
{% tab title="200: OK Successful operation" %}
{% tabs %}
{% tab title="Schema" %}
```plsql
id string
source_url string
update_frequency string
last_cached string
```
{% endtab %}

{% tab title="Example" %}
```json
[{'id': 'rec0Fh8dMrlfxlpoH', 'source_url': 'https://www.portlandmaine.gov/999/Annual-Reports', 'update_frequency': 'Annually', 'last_cached': '2024-01-30'}]
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="400: Bad Request Missing or bad API key" %}
{% tabs %}
{% tab title="Schema" %}
```plsql
string
```
{% endtab %}

{% tab title="Example" %}
```json
"There has been an error pulling data!"
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="403: Forbidden Invalid API key" %}

{% endtab %}
{% endtabs %}

## Get all Archived urls

<mark style="color:orange;">`PUT`</mark> `[base-url]/archives`

The archives endpoint is located in [resources/Archives.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/Archives.py). The put method on the archives endpoint updates the data source matching the passed id, updating the last\_cached date if it alone is passed, or it and the broken\_source\_url\_as\_of field and the url\_status to 'broken'.&#x20;

#### Headers

| Name                                            | Type   | Description                                         |
| ----------------------------------------------- | ------ | --------------------------------------------------- |
| Authorization<mark style="color:red;">\*</mark> | String | Value formatted as "Bearer \[access token/api key]” |

#### Request Body

| Name                                                          | Type   | Description                                                                        |
| ------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------- |
| id<mark style="color:red;">\*</mark>                          | String | The airtable uid for the data source that was cached                               |
| broken\_source\_url\_as\_of<mark style="color:red;">\*</mark> | Date   | The current date if the url is no longer active, otherwise None                    |
| last\_cached<mark style="color:red;">\*</mark>                | Date   | The current date since the data source url was just cached in the Internet Archive |

{% tabs %}
{% tab title="200: OK Successful operation" %}
{% tabs %}
{% tab title="Schema" %}
<pre class="language-plsql"><code class="lang-plsql">count int
<strong>data array[object]
</strong>    agency_name string
    municipality string
    state_iso string
    data_source_name string
    description string
    record_type string
    source_url string
    record_format string
    coverage_start string
    coverage_end string
    agency_supplied boolean
</code></pre>
{% endtab %}

{% tab title="Example" %}
```json
{
	"count": 1,
	"data": [
		{
			"agency_name": "Allegheny County Police Department - PA",
			"municipality": "Pittsburgh",
			"state_iso": "PA",
			"data_source_name": "Allegheny County Police Review Board Transcripts",
			"description": null,
			"record_type": "Policies & Contracts",
			"source_url": "https://www.alleghenycounty.us/county-council/police-review-board-meetings.aspx",
			"record_format": "[\"PDF: Machine Created\"]",
			"coverage_start": "2018-08-29",
			"coverage_end": "2018-09-26",
			"agency_supplied": true
		}
	]
}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="400: Bad Request Missing or bad API key" %}

{% endtab %}

{% tab title="403: Forbidden Invalid API key" %}

{% endtab %}
{% endtabs %}

## Agencies

## Get all Agencies

<mark style="color:blue;">`GET`</mark> `[base-url]/agencies/{page}`

The agencies endpoint is located in [resources/Agencies.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/QuickSearch.py). The agencies endpoint returns 1000 rows from the corresponding Data Sources database table offset by the page number passed.

#### Path Parameters

| Name                                   | Type   | Description                                                                                  |
| -------------------------------------- | ------ | -------------------------------------------------------------------------------------------- |
| page<mark style="color:red;">\*</mark> | String | Passing 1 will return the first 1000 rows. Subsequent page number return  subsequent results |

#### Headers

| Name          | Type   | Description                                         |
| ------------- | ------ | --------------------------------------------------- |
| Authorization | String | Value formatted as "Bearer \[access token/api key]” |

{% tabs %}
{% tab title="200: OK Successful operation" %}
{% tabs %}
{% tab title="Schema" %}
<pre class="language-plsql"><code class="lang-plsql">count int
<strong>data array[object]
</strong>    agency_name string
    municipality string
    state_iso string
    data_source_name string
    description string
    record_type string
    source_url string
    record_format string
    coverage_start string
    coverage_end string
    agency_supplied boolean
</code></pre>
{% endtab %}

{% tab title="Example" %}
```json
{
	"count": 1,
	"data": [
		{
			"agency_name": "Allegheny County Police Department - PA",
			"municipality": "Pittsburgh",
			"state_iso": "PA",
			"data_source_name": "Allegheny County Police Review Board Transcripts",
			"description": null,
			"record_type": "Policies & Contracts",
			"source_url": "https://www.alleghenycounty.us/county-council/police-review-board-meetings.aspx",
			"record_format": "[\"PDF: Machine Created\"]",
			"coverage_start": "2018-08-29",
			"coverage_end": "2018-09-26",
			"agency_supplied": true
		}
	]
}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="400: Bad Request Missing or bad API key" %}
{% tabs %}
{% tab title="Schema" %}
```plsql
count int
data array[object]
```
{% endtab %}

{% tab title="Example" %}
```json
{
	"count": 0,
	"data": []
}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="403: Forbidden Invalid API key" %}

{% endtab %}
{% endtabs %}
