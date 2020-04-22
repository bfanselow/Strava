# Strava

## Collection of scripts/modules for accessing Strava API
---
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


---
### Authentication
Strava uses OAuth to allow third-party services access to a user’s data. This involves the following steps:
 1. Service calls Strava with a CLIENT_ID and a redirect-URL.
 2. The user is presented with a Strava authentication page which for granting access to the service including specifiyng scope of authentication.
 3. Strava auth redirects the user's browser back to the service (redirect-URI) with a an **access-code**.
 4. The service sends this access-code (along with client-id, and client-secret) to recieve a short-lived **access-token** and **refresh-token**. 

With this **access-token**, the service now has access to the user's Strava data using the access-token within the scope granted. 

---
### Generating access-token for development cycles 
Due to the OAuth mechanism above, in order to write and test code for API-access scripts we need a method of obtaining the access-token. This can be done by setting up a simple web/api service (see below), or this can be done by by manually stepping through the 4-step authentication process above as follows:
  1. In a browser, hit the URL (where scope is the requested access-scope such as *activity:read_all*)
```
https://www.strava.com/oauth/authorize?client_id=[CLIENT_ID]&redirect_uri=http://[CALLBACK_DOMAIN]&response_type=code&scope=[SCOPE]
```
  2. This will present a Strava authentication session asking for permission for Strava to authorize the service's access to user data.
  3. Upon submit, the browsers will be redirected to the redirect_URI.  For development purposes the response is found in the browser address bar.  From this response, copy the **ACCESS_CODE**
```
http://[CALL_BACK_DOMAIN]/?state=&code=[ACCESS_CODE]&scope=[SCOPES]
```
  4. Make a POST request with a (json) payload containing **CLIENT_ID, CLIENT_SECRET, ACCESS_CODE**, and **grant_type=authorization_code** to the following URL. The response to this request will contain an **access-token** and a **refresh-token**.
```
https://www.strava.com/oauth/token
```
Example curl POST (using access-code to retrieve access-token):
```
json="{\"client_id\":\"${CLIENT_ID}\", \"client_secret\":\"${CLIENT_SECRET}\", \"code\":\"${CODE}\", \"grant_type\":\"authorization_code\"}"
echo "JSON: $json"
/usr/bin/curl -d "$json" -H 'Content-Type: application/json' https://www.strava.com/oauth/token
```
---
## Using a simple Python API service to get the access-token
 1. Populate **auth.json** file:    
    { "client_id": "<cid>", "client_secret": "<secret>", "access_token": "<token>", "refresh_token": "<token>" }   
    (where access_token here is the default, limited-scope token created on application-api registration) 
 2. Execute **./strava_api_service.py**
```
  (venv) $ ./strava_api_service.py
```
 3. Open a browser to the *ip:port* configured in the strava_api_service.py script (i.e. http://localhost:8080)
 4. Got to **http://localhost:8080/authorize** which will automatically take you though the OAuth steps and finally return an access_token 
