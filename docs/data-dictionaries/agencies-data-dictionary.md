# Agencies data dictionary

{% hint style="info" %}
To see which options are available for select fields, consult the [submission form](https://airtable.com/shrzxLdSsYmBvIWMH).
{% endhint %}

### Required properties for submission

`submitter_contact`, `submitted_name`, `homepage_url`, `jurisdiction_type`, `agency_type`, + geographic info dependent on the `jurisdiction_type`.

## Identification & web presence

| Property          | Type    | Description                                                                                                                                                                                                                    |
| ----------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| name              | string  | If a `state` is present, concatenates `submitted_name` + `" - "` + `state_iso` to help differentiate agencies with similar names in some Airtable menus. Otherwise, uses `submitted_name`.                                     |
| submitted\_name   | string  | What does the agency call itself?                                                                                                                                                                                              |
| agency\_type      | string  | Options include `law enforcement/police`, `court`, and `corrections`.                                                                                                                                                          |
| multi\_agency     | boolean | True for utility agencies, used to geolocate data sources which cover multiple agencies. For example, a source about the "Allegheny County Aggregated" multi-agencies contains records about all agencies in Allegheny County. |
| defunct\_year     | integer | If present, denotes an agency which has defunct but may still have relevant records.                                                                                                                                           |
| homepage\_url     | string  | A URL for the homepage of this agency.                                                                                                                                                                                         |
| no\_web\_presence | boolean | True when an agency does not have a dedicated website.                                                                                                                                                                         |

## Geographic

| Property           | Type                                          | Description                                                                                          |
| ------------------ | --------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| jurisdiction\_type | string                                        | What is the highest level of jurisdiction for the agency? Can be an option like `local` or `county`. |
| state\_iso         | string                                        | 2-character ISO code. Does not apply to federal agencies.                                            |
| county\_fips       | string (not an integer because of leading 0s) | Unique 5-digit code to identify counties. Does not apply to state or federal agencies.               |
| county\_name       | string                                        | Official County name. Does not apply to state or federal agencies.                                   |
| municipality       | string                                        | Official municipality name. Does not apply to county, state, or federal agencies.                    |
| zip\_code          | string (not an integer because of leading 0s) | Postal code for the agency's headquarters.                                                           |
| lat                | float                                         | Geographic latitude for the agency's headquarters.                                                   |
| lng                | float                                         | Geographic longitude for the agency's headquarters.                                                  |

## Meta & utility

| Property      | Type   | Description                                               |
| ------------- | ------ | --------------------------------------------------------- |
| airtable\_uid | string | The Airtable-generated UID of this particular data source |
