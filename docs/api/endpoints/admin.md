---
description: Use the API to managing users, keys, and access as PDAP staff
---

# Admin

## Base URL

```
https://data-sources.pdap.io
```

## Login & API keys

## Creates a new user.

<mark style="color:green;">`POST`</mark> `[base-url]/user`

Users can sign up for an account through the post function in [resources/User.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/User.py). The user's password is hashed using werkzeug.security’s generate\_pasword\_hash function. The user's email and hashed password is stored in the users table in the Data Sources database.

#### Request Body

| Name                                       | Type   | Description                   |
| ------------------------------------------ | ------ | ----------------------------- |
| email<mark style="color:red;">\*</mark>    | String | User's email - must be unique |
| password<mark style="color:red;">\*</mark> | String | User's password               |

{% tabs %}
{% tab title="201: Created User successfully created" %}
{% tabs %}
{% tab title="Schema" %}
```plsql
message string
```
{% endtab %}

{% tab title="Example" %}
```json
{
    "message": "Successfully added user"
}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="500: Internal Server Error Error" %}

{% endtab %}

{% tab title="401: Unauthorized Login failed" %}
```javascript
{
    // Response
}
```
{% endtab %}
{% endtabs %}



## Updates user password.

<mark style="color:orange;">`PUT`</mark> `[base-url]/user`

Users can update their password through the put function in [resources/User.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/User.py). The user's password is hashed using werkzeug.security’s generate\_pasword\_hash function. The user's email and hashed password is stored in the users table in the Data Sources database.

#### Request Body

| Name                                       | Type   | Description                   |
| ------------------------------------------ | ------ | ----------------------------- |
| email<mark style="color:red;">\*</mark>    | String | User's email - must be unique |
| password<mark style="color:red;">\*</mark> | String | User's password               |

{% tabs %}
{% tab title="201: Created User password successfully updated" %}
{% tabs %}
{% tab title="Schema" %}
```plsql
message string
```
{% endtab %}

{% tab title="Example" %}
```json
{
    "message": "Successfully updated password"
}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="500: Internal Server Error Error" %}

{% endtab %}
{% endtabs %}

## Logs in the user.

<mark style="color:green;">`POST`</mark> `[base-url]/login`

The login function can be found through the get function in [resources/Login.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/Login.py). If the email and password match a row in the database, "Successfully logged in" will be returned.

#### Request Body

| Name                                       | Type   | Description                                                                                                                                   |
| ------------------------------------------ | ------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| email<mark style="color:red;">\*</mark>    | String | Matches exactly with the "email" property in user's table                                                                                     |
| password<mark style="color:red;">\*</mark> | String | Checked against the password\_digest for the user with the matching "email" property using werkzeug.security’s check\_password\_hash function |

{% tabs %}
{% tab title="200: OK Successful login" %}
{% tabs %}
{% tab title="Schema" %}
```plsql
message string
data string
```
{% endtab %}

{% tab title="Example" %}
```json
{
    "message": "Successfully logged in"
    "data": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDg3MDE4MjksImlhdCI6MTcwODcwMTUyOSwic3ViIjo2NX0.Fuue4oDXFlS4N_AS41N2dchvMXGEihhpVdrhwxCf8zA"
}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="400: Bad Request Missing or bad API key" %}

{% endtab %}

{% tab title="403: Forbidden " %}
```javascript
{
    // Response
}
```
{% endtab %}

{% tab title="500: Internal Server Error Error" %}
```javascript
{
    // Response
}
```
{% endtab %}
{% endtabs %}

## Refreshes the user's session token.

<mark style="color:green;">`POST`</mark> `[base-url]/refresh-session`

The logic can be found in the post function in [resources/RefreshSession.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/RefreshSession.py). If the old session token matches a row in the database, "Successfully refreshed session token" will be returned.

#### Request Body

| Name                                       | Type   | Description                                                                                                                                   |
| ------------------------------------------ | ------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| email<mark style="color:red;">\*</mark>    | String | Matches exactly with the "email" property in user's table                                                                                     |
| password<mark style="color:red;">\*</mark> | String | Checked against the password\_digest for the user with the matching "email" property using werkzeug.security’s check\_password\_hash function |

{% tabs %}
{% tab title="200: OK Successful session refresh" %}
{% tabs %}
{% tab title="Schema" %}
```plsql
message string
data string
```
{% endtab %}

{% tab title="Example" %}
```json
{
    "message": "Successfully refreshed session token"
    "data": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDg3MDE4MjksImlhdCI6MTcwODcwMTUyOSwic3ViIjo2NX0.Fuue4oDXFlS4N_AS41N2dchvMXGEihhpVdrhwxCf8zA"
}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="403: Forbidden Invalid old session token" %}
```javascript
{
    // Response
}
```
{% endtab %}

{% tab title="500: Internal Server Error Error" %}
```javascript
{
    // Response
}
```
{% endtab %}
{% endtabs %}

## Sends user a password reset link.

<mark style="color:blue;">`POST`</mark> `[base-url]/request-reset-password`

This functionality can be found in the get function in [resources/RequestResetPassword.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/tree/main/resources/RequestResetPassword.py). If the email and password match a row in the database, "Successfully logged in" will be returned.

#### Request Body

| Name                                    | Type   | Description                                               |
| --------------------------------------- | ------ | --------------------------------------------------------- |
| email<mark style="color:red;">\*</mark> | String | Matches exactly with the "email" property in user's table |

{% tabs %}
{% tab title="200: OK Successful reset request" %}

{% endtab %}

{% tab title="500: Internal Server Error Error" %}

{% endtab %}
{% endtabs %}

## Sends user a password reset link.

<mark style="color:blue;">`POST`</mark> `[base-url]/request-reset-password`

This functionality can be found in the get function in [resources/RequestResetPassword.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/tree/main/resources/RequestResetPassword.py). If the email and password match a row in the database, "Successfully logged in" will be returned.

#### Request Body

| Name                                    | Type   | Description                                               |
| --------------------------------------- | ------ | --------------------------------------------------------- |
| email<mark style="color:red;">\*</mark> | String | Matches exactly with the "email" property in user's table |

{% tabs %}
{% tab title="200: OK Successful reset request" %}
{% tabs %}
{% tab title="Schema" %}
```plsql
message string
```
{% endtab %}

{% tab title="Example" %}
```json
{
    "message": "An email has been sent to your email address with a link to reset your password."
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDg3MDE4MjksImlhdCI6MTcwODcwMTUyOSwic3ViIjo2NX0.Fuue4oDXFlS4N_AS41N2dchvMXGEihhpVdrhwxCf8zA"
}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="500: Internal Server Error Error" %}

{% endtab %}
{% endtabs %}

## Reset password token check.

<mark style="color:blue;">`POST`</mark> `[base-url]/reset-token-validation`

This functionality can be found in the get function in [resources/ResetTokenValidation.py](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/RequestResetPassword.py). If the token matches a row in the database, "Token is valid" will be returned.

#### Path Parameters

| Name                                    | Type   | Description          |
| --------------------------------------- | ------ | -------------------- |
| token<mark style="color:red;">\*</mark> | String | Reset password token |

{% tabs %}
{% tab title="200: OK Reset password token validated" %}
{% tabs %}
{% tab title="Schema" %}
```plsql
message string
```
{% endtab %}

{% tab title="Example" %}
```json
{
    "message": "The submitted token is valid"
}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="400: Bad Request Token is invalid" %}
{% tabs %}
{% tab title="Schema" %}
```plsql
message string
```
{% endtab %}

{% tab title="Example" %}
```json
{
    "message": "The submitted token is invalid"
}
```
{% endtab %}
{% endtabs %}
{% endtab %}

{% tab title="500: Internal Server Error Error" %}
```javascript
{
    "message": "error"
}
```
{% endtab %}
{% endtabs %}

## Returns an API key for a valid user and password.

<mark style="color:blue;">`GET`</mark> `[base-url]/api_key`

The key generation function can be found through the get function in [resources/ApiKey](https://github.com/Police-Data-Accessibility-Project/data-sources-app/blob/main/resources/ApiKey.py). If the email and password match a row in the database, a new API key is created using uuid.uuid4().hex, updated in for the matching user in the users table, and the API key is sent to the user.

#### Request Body

| Name                                       | Type   | Description                                                                                                                                   |
| ------------------------------------------ | ------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| email<mark style="color:red;">\*</mark>    | String | Matches exactly with the "email" property in user's table                                                                                     |
| password<mark style="color:red;">\*</mark> | String | Checked against the password\_digest for the user with the matching "email" property using werkzeug.security’s check\_password\_hash function |

{% tabs %}
{% tab title="200: OK Successful login" %}
{% tabs %}
{% tab title="Schema" %}
```plsql
api_key string
```
{% endtab %}

{% tab title="Example" %}
```json
{
	"api_key": "2bd77a1d7ef24a1dad3365b8a5c6994e"
}
```
{% endtab %}
{% endtabs %}
{% endtab %}
{% endtabs %}
