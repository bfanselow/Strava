# Strava

## Collection of scripts/modules for access Strava API

### API Application
Strava provides API access to user data via an **API Application**. Registering an **API Application** is done on the Strava UI portal.
The following fields are required for registration of an API Application:
  - Application Name: this is an arbitrary identification for the service which will be accessing the data.
  - Category: ???
  - Website:  this the URL for the service performing the API access. (Use *https://strava.com* for basic script development)
  - Application Description:  
  - Authorization Callback Domain:  this the **redirect-URI** used by the OAuth process described below. (Use *localhost* for basic script development)

Upon registration of an **API Application**, your App will have the following default parameters:
  * CLIENT_ID:  API-application **id** used by all API authentication sessions (described below)
  * CLIENT_SECRET: API-application **secret** used by all API authentication sessions 
  * ACCESS_TOKEN:  Inital access-token for API access scope. Provides very limited access scope
  * REFRESH_TOKEN: Used for re-generating new (limited-scope) access token.


### Authentication
Strava uses OAuth to allow third-party services access to a user’s data. This involves the following steps:
 1. Service calls Strava with a CLIENT_ID and with a redirect-URL.
 2. The user is authenticates with Strava auth server including specifiyng scope of authentication.
 3. Strava auth redirects the user's browser back to the service with a short-lived access-token and a refresh-token.
 4. The service now has access to the user's Strava data within the scope granted. 


### API Developer access
Due to the OAuth mechanism above, in order to write and test code for API-access scripts we need will set up a simple web server.  It is possible to manually run through the 4-step process above as follows:
  1. In a browser, hit the URL: **https://www.strava.com/oauth/authorize?client_id=[CLIENT_ID]&redirect_uri=http://[CALLBACK_DOMAIN]&response_type=code&scope=[SCOPE]** (where scope is access-scope such as *activity:read_all*)
  2. This will present a Strava authentication session asking for permission for Strava to authorize the service's access to user data.
  3. Upon submit, the browsers will be redirected to the redirect_URI.  For development purposes the response is found in the browser address bar: **http://[CALL_BACK_DOMAIN]/?state=&code=[ACCESS_CODE]&scope=[SCOPES]**   
     Copy the **ACCESS_CODE**
  4. Make a POST request to **https://www.strava.com/oauth/token** with json payload containing CLIENT_ID, CLIENT_SECRET, ACCESS_CODE, and "grant_type=authorization_code"
Example curl POST:
```
json="{\"client_id\":\"${CLIENT_ID}\", \"client_secret\":\"${CLIENT_SECRET}\", \"code\":\"${CODE}\", \"grant_type\":\"authorization_code\"}"
echo "JSON: $json"
/usr/bin/curl -d "$json" -H 'Content-Type: application/json' https://www.strava.com/oauth/token
```
