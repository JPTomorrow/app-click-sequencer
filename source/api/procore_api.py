'''
    Author: Justin Morrow
    Date created: 4/20/2021
    Python Version: 3.4
    Description: A Module to interface with the Procore REST API
'''

import requests
from source.api.api_error import ApiError
from os import path
import json
import urllib
from flask import request, Flask
import webbrowser

import click
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

""" Procore OAuth """

class ProcoreOAuth():
    def __init__(self, sandbox = False):
        self.ClientID = ''
        self.ClientSecret = ''
        self.RedirectURI = []
        self.OAuthURL = ''
        self.BaseURL = ''
        self.AccessToken = ''
        self.RefreshToken = ''
        self.TokenCreationTime = ''
        self.IsAuthorized = False

        # start flask server to prompt user with auth url and get callback
        self.OAuthWebPresenter = Flask(__name__)

        # read client credentials from json file on system
        # @TODO: replace with more secure method of storing client secret
        creds_fname = 'creds/creds.json'

        if (path.exists(creds_fname)):
            self.read_creds_from_file(creds_fname, sandbox)
        else:
            print('credentials file path did not exist at {}'.format(creds_fname))
            return

        # prompt user for credentials and authorize
        self.authenticate_user()

    def authenticate_user(self):
        params = {
            "client_id": self.ClientID,
            "response_type" : "code"
        }

        auth_url = self.OAuthURL + '/oauth/authorize?' \
            + urllib.parse.urlencode(params) \
            + '&redirect_uri=' + self.RedirectURI[0]

        webbrowser.open(auth_url)

        # This is a localhost flask server to handle the redirect from the oauth
        # It will call get_auth_token() after the callback link has been visited
        # and retrieve the access token
        @self.OAuthWebPresenter.route('/')
        def index():
            return 'This is a listening flask server for procore login'

        @self.OAuthWebPresenter.route('/callback/', methods=["GET"])
        def redirect_callback():
            code = request.args.get('code')
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
            return ("User is authenticated. You can close this browser window and return to the application.", self.get_auth_token(code))  # send text to web browser
        
        # disable logging to console completely for flask server
        def secho(text, file=None, nl=None, err=None, color=None, **styles):
            pass

        def echo(text, file=None, nl=None, err=None, color=None, **styles):
            pass

        click.echo = echo
        click.secho = secho

        #launch flask server and wait for redirect
        self.OAuthWebPresenter.run(port=8000, debug=False)

        # The user should be authrorized and have an access token 
        # at this point due to the flask server callback
        self.IsAuthorized = True
    
    def get_auth_token(self, auth_code):
        if auth_code == '':
            self.IsAuthorized = False
            return

        client_auth = requests.auth.HTTPBasicAuth(self.ClientID, self.ClientSecret)
        post_data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.RedirectURI[0]
        }
        
        response = requests.post(self.BaseURL+"/oauth/token",
                                auth=client_auth,
                                data=post_data)
        response_json = response.json()

        self.AccessToken = response_json["access_token"]
        self.RefreshToken = response_json["refresh_token"]
        self.TokenCreationTime = response_json['created_at']

    def revoke_token(self, token: str):
        body = {
            "token" : token,
            "client_id" : self.ClientID,
            "client_secret" : self.ClientSecret
        }

        resp = requests.post(self.BaseURL + "/oauth/revoke", json=body)
        status = resp.status_code
        if status == 200: self.IsAuthorized = False
        return status

    def read_creds_from_file(self, filename, sandbox = False):
        f = open(filename)
        data = json.load(f)

        if (sandbox):
            self.ClientID = data['sandbox']['client_id']
            self.ClientSecret = data['sandbox']['client_secret']
            self.OAuthURL = data['sandbox']['oauth_url']
            self.BaseURL = data['sandbox']['base_url']
            self.RedirectURI = data['sandbox']['redirect_uri']
        else:
            self.ClientID = data['real']['client_id']
            self.ClientSecret = data['real']['client_secret']
            self.OAuthURL = data['real']['oauth_url']
            self.BaseURL = data['real']['base_url']
            self.RedirectURI = data['real']['redirect_uri']
        
    def to_string(self):
        o = '\nClient Credentials-------------'
        o += '\nClient ID: {}\nClient Secret: {}\nRedirect URI: {}\nOAuth URL: {}\nBase URL: {}\n' \
            .format(self.ClientID, self.ClientSecret, self.RedirectURI, self.OAuthURL, self.BaseURL)
        o += '\n'
        return o

""" Procore Client """

class ProcoreClient:
    def __init__(self, credentials: ProcoreOAuth):
        if credentials.IsAuthorized:
            self.Credentials = credentials
        else:
            raise ApiError('Provided credentials are not authorized for use with this client.')

    def print_creds(self):
        print(self.Credentials.to_string())

    def test_request(self):
        resp = requests.get('https://api.github.com')

        if (resp.status_code != 200):
            raise ApiError("Invalid Response Code")
        print(resp.json())

        """ for item in resp.json():
            print('{} {}'.format(item['id'], item['summary'])) """

    def sandbox_test(self):
        pass
        """ #url = self.Credentials.OAuthURL + '/oauth/authorize?' + urllib.parse.urlencode(params)
        resp = requests.get(url, params)

        if (resp.status_code != 200):
            raise ApiError("Invalid Response Code")
            
        for item in resp.json():
            print('{} {}'.format(item['id'], item['summary'])) """

    # get your current user info
    def get_me(self):
        if not self.Credentials.IsAuthorized: return {}
        headers = {
            "access_token" : self.Credentials.AccessToken
        }

        resp = requests.get(self.Credentials.BaseURL + '/rest/v1.0/me', headers)
        j = resp.json()
        return j

    # get the current users ID
    def get_current_user_id(self):
        if not self.Credentials.IsAuthorized: return None
        json = self.get_me()
        return json['id']

    # get all available projects for the current user
    def get_me_projects(self):
        headers = {
            "access_token" : self.Credentials.AccessToken
        }

        resp = requests.get(self.Credentials.BaseURL + '/rest/v1.0/projects', headers)
        j = resp.json()
        return j

    # get a list of all the companies the current user can see
    def get_user_companies(self):
        if not self.Credentials.IsAuthorized: return {}

        headers = {
            "access_token" : self.Credentials.AccessToken
        }

        resp = requests.get(self.Credentials.BaseURL + '/rest/v1.0/companies', headers)
        j = resp.json()
        return j

    # get all projects visible to the provided company id
    def get_projects_by_company_id(self, company_id):
        if not self.Credentials.IsAuthorized: return None
        headers = {
            "access_token" : self.Credentials.AccessToken,
            "company_id" : company_id
        }

        resp = requests.get(self.Credentials.BaseURL + '/rest/v1.0/projects', headers)
        j = resp.json()
        return j



    