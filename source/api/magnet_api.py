from flask.helpers import send_file
from flask import request, Flask
import requests
import json
import urllib
import webbrowser
import click

class MagnetSSO():
    def __init__(self): 
        self.BaseApiUrl = 'https://mdc-stable.magnet-cloud.com/v7'
        self.SSOLoginUrl = 'https://api.topcon.com/login'
        self.RedirectUri = 'http://127.0.0.1:8000/callback/'
        self.SSOAuthSuffix = '/auth/sso'
        self.AccessToken = ''
        self.IsAuthorized = False
        # self.send_auth_request()
        self.flask_sso_prompt_user()

    def send_auth_request(self):
        code = {
            "authorizationCode" : "abc"
        }

        response = requests.post(self.BaseApiUrl + self.SSOAuthSuffix, data=code)
        resp_json = response.json()
        print(resp_json)

    def flask_sso_prompt_user(self):
        #params = {
        #    "client_id": self.ClientID,
        #    "response_type" : "code"
        #}

        # start flask server to prompt user with auth url and get callback
        self.OAuthWebPresenter = Flask(__name__)

        auth_url = self.SSOLoginUrl + '/?redirect_uri=' + self.RedirectUri[0]
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
        if self.AccessToken != '': self.IsAuthorized = True

    def get_auth_token(self, auth_code):
        if auth_code == '':
            self.IsAuthorized = False
            return

        #client_auth = requests.auth.HTTPBasicAuth(self.ClientID, self.ClientSecret)
        code_data = { "authorizationCode": auth_code, }
        response = requests.post(self.BaseURL+"/auth/sso", data=code_data)
        response_json = response.json()
        self.AccessToken = response_json["access_token"]



