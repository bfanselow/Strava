#!/usr/bin/env python
"""

  File: strava_api_service.py
  Description:
    Simple API for exposing several Strava API-access methods including
    processing the Strava OAuth steps to get a "scoped" access_token

  Usage: 
   1) Populate "auth.json" file with JSON format (where access_token is the default-scope level token): 
         { "client_id": "<cid>", "client_secret": "<secret>", "access_token": "<token>", "refresh_token": "<token>" } 
      These come from your Applciation-API registration.
   2) Execute: $ ./strava_api_service.py

  Available routes:
   * /           => basic index/home page
   * /clientid   => show client_id 
   * /profile    => show user profile associated with client_id 
                    (requires valid default-access-token. Use /refresh to refresh it and update auth.json) 
   * /refresh    => refresh default-level access-token 
   * /authorize  => perform the Strava OAuth process:
       1) redirect to Strava auth page 
       2) users submits auth confirmation 
       3) Strava auth server redirects to this site's "/authoriztion_success" route - request params contain "code" 
       4) Send request back to Strava auth server with "code" to retrieve an "access_token" 

  Notes:
   * Inspired by: https://github.com/sladkovm/strava-oauth
   * Running api.run() creates "static" dir in current dir 

"""

import responder
import requests
import os
import json
import urllib
import logging

APP_URL = 'http://localhost'

PORT = 5042 

## Strava Base URL's
STRAVA_URL = "http://www.strava.com"
STRAVA_OAUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_ATHLETE_URL = "https://www.strava.com/api/v3/athlete"

## local auth file in json format 
AUTH_FILE = './auth.json'

## Set up the responder-API
api = responder.API()

##-----------------------------------------------------------------------------------
class AuthError(Exception):
  pass

##-----------------------------------------------------------------------------------
def load_auth_credentials(auth_file_path):
  """
   Read the auth-credential file and load the client-id and client-secret .
   File should have json format:
     { "client_id": "<cid>", "client_secret": "<secret>", "access_token": "<token>", "refresh_token": "<token>" } 

   Required args: path to auth_file
   Return (tuple): client_id, client_secret
  """
  print("Loading auth file data: %s..." % (auth_file_path))

  if not os.path.exists(auth_file_path):
    raise AuthError("Auth file not found: [%s]" % (auth_file_path))
  if not os.access(auth_file_path, os.R_OK):
    raise AuthError("Auth file cound not be read: [%s]" % (auth_file_path))

  with open(auth_file_path) as f:
    data = json.load(f) 

    client_id = data.get('client_id', None)
    client_secret = data.get('client_secret', None)
    access_token = data.get('access_token', None)
    refresh_token = data.get('refresh_token', None)
    if not client_id:
      raise AuthError("%s: Failed to retrieve auth value: [client_id]")
    if not client_secret:
      raise AuthError("%s: Failed to retrieve auth value: [client_secret]")
    if not access_token:
      raise AuthError("%s: Failed to retrieve auth value: [access_token]")
    if not refresh_token:
      raise AuthError("%s: Failed to retrieve auth value: [refresh_token]")

  return( client_id, client_secret, access_token, refresh_token )


##-----------------------------------------------------------------------------------
def get_authorization_url():
    """Generate authorization url"""
    logging.info("Generating authorization url...")
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": f"{APP_URL}:{PORT}/authorization_success", 
        "scope": "read,profile:read_all,activity:read",
        "state": STRAVA_URL,
        "approval_prompt": "force"
    }
    params_str = urllib.parse.urlencode(params)
    url = STRAVA_OAUTH_URL + '?' + params_str 
    logging.info("Authorization-URL: %s" % (url))
    return( url )


##-------------------------------
## Route handers
##-------------------------------
@api.route("/")
def home(req, resp):
    """Simple index page"""
    output = "Strava OAuth Service Routes:<br><ul>"
    output += "<li>/clientid"
    output += "<li>/profile"
    output += "<li>/refresh"
    output += "<li>/authorize"
    resp.html = output 

##-------------------------------
@api.route("/clientid")
def clientid(req, resp):
    logging.info("Show client id...")
    resp.text = "CLIENT_ID=%s" % (CLIENT_ID)

##-------------------------------
@api.route("/profile")
def profile(req, resp):
    logging.info("Getting athlete profile...")
    d_headers = { "Authorization": "Bearer %s" % (DEFAULT_TOKEN) }
    r = requests.get(url=STRAVA_ATHLETE_URL, headers=d_headers)
    logging.info(r.text)
    resp.text = r.text

##-------------------------------
@api.route("/refresh")
def refresh(req, resp):
    """Refresh default access_token"""
    logging.info("Refreshing default access_token...")
    d_params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN, 
        "grant_type": "refresh_token"
    }
    r = requests.post(url=STRAVA_TOKEN_URL, params=d_params)
    resp.text = r.text

##-------------------------------
@api.route("/authorize")
def authorize(req, resp):
    """Redirect user to the Strava OAuth Authorization page"""
    redirect = get_authorization_url()
    logging.info("Redirecting to Strava OAuth page...")
    api.redirect(resp, location=redirect)

##-------------------------------
@api.route("/authorization_success")
def authorization_success(req, resp):
    """For internal OAuth process only - get code from request params and send new request for access_token"""
    logging.info("Got response from Strava OAuth page")
    code = req.params.get('code')
    d_params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    }
    r = requests.post(url=STRAVA_TOKEN_URL, params=d_params)
    logging.info(r.text)
    resp.text = r.text

##-----------------------------------------------------------------------------------
if __name__ == "__main__":
    (CLIENT_ID, CLIENT_SECRET, DEFAULT_TOKEN, REFRESH_TOKEN) = load_auth_credentials(AUTH_FILE)
    print("Starting server...")
    api.run(address="0.0.0.0", port=PORT)
