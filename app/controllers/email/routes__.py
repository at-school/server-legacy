# -*- coding: utf-8 -*-
from __future__ import print_function
import flask
from oauth2client import file, client, tools

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import json
import os
from flask_cors import CORS
import requests
from authentication import auth
from flask import Flask, redirect, request, jsonify, session, url_for
from googleapiclient.discovery import build
from httplib2 import Http

from app.controllers.email import bp

CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = ["https://mail.google.com/"]
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

app = Flask(__name__)
app.secret_key = 'far out making this mail appliaction is impossible'
app.debug = True
CORS(app)

@bp.route('/')
def index():
  return ''

@bp.route('/testAuth')
def runAuthTest():
	service = auth()
	return 'auth ok ;)'

@bp.route('/test', methods=['GET', 'POST'])
def test_api_request():

	if 'credentials' not in session:
		return redirect('authorize')
	credentials = google.oauth2.credentials.Credentials(
		**session['credentials'])
	service = googleapiclient.discovery.build(
		API_SERVICE_NAME, API_VERSION, credentials=credentials)
	files = service.users().messages().list(userId="me",
							labelIds=["INBOX"], maxResults=20 ).execute()
	for attr, value in credentials.__dict__.items():
		print(attr, value)
	cred = credentials_to_dict(credentials)
	a = open('token_.json').read()
	b = json.loads(a)
	for key, val in cred.items():
		if key == 'token':
			b['access_token'] = val
			b["token_response"]["access_token"] = val
		else:
			b[key] = val
	json.dump(b, open('token.json', 'w'))
	session['credentials'] = cred
	return jsonify(**files)

@bp.route('/authorize', methods=['POST', "GET"])
def authorize():
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
		CLIENT_SECRETS_FILE, scopes=SCOPES)
	flow.redirect_uri = url_for('oauth2callback', _external=True)
	authorization_url, state = flow.authorization_url(
										access_type='offline')
	session['state'] = state
	print("Url", authorization_url)
	print('got here')
	return redirect(authorization_url, redirect_uri)
	# return jsonify({"link": authorization_url})

@bp.route('/oauth2callback', methods=['GET', 'POST'])
def oauth2callback():
	state = session['state']
	print('here')
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
		CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
	print('here1')
	flow.redirect_uri = url_for('oauth2callback', _external=True)
	print('here2')
	print('REQUEST')
	authorization_response = request.url
	print('here3')
	print("RESPONSE",authorization_response)
	flow.fetch_token(authorization_response=authorization_response)
	print('here4')
	credentials = flow.credentials
	print('here5')
	session['credentials'] = credentials_to_dict(credentials)
	print('here6')
	return redirect(url_for('test_api_request'))

@bp.route('/revoke', methods=['GET', 'POST'])
def revoke():
	if 'credentials' not in session:
		return ('You need to <a href="/authorize">authorize</a> before '
				+ 'testing the code to revoke credentials.')
	credentials = google.oauth2.credentials.Credentials(
		**session['credentials'])
	revoke = requests.post('https://accounts.google.com/o/oauth2/revoke'
		,params={'token': credentials.token},
		headers = {'content-type': 'application/x-www-form-urlencoded'})
	status_code = getattr(revoke, 'status_code')
	if status_code == 200:
		return 'Credentials successfully revoked.'
	else:
		return 'An error occurred.'

@bp.route('/clear')
def clear_credentials():
	if 'credentials' in session:
		session.clear()
	return 'Credentials have been cleared.'

def credentials_to_dict(credentials):
	return {'token': credentials.token,
				'refresh_token': credentials.refresh_token,
				'token_uri': credentials.token_uri,
				'client_id': credentials.client_id,
				'client_secret': credentials.client_secret,
				}

if __name__ == '__main__':
	# When running locally, disable OAuthlib's HTTPs verification.
	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
	app.run('localhost', 8080, debug=False)
