from __future__ import print_function
import flask
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import json
import os
import requests
from flask import Flask, redirect, request, jsonify, session, url_for
from googleapiclient.discovery import build
from httplib2 import Http
from app.controllers.email.authentication import auth
from app.controllers.email.PyMail import Gmail, GetMessages
from app.controllers.email.MailLogging import debug

from flask_jwt_extended import jwt_required

from app.controllers.email import bp

import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

DIR_ = "app/controllers/email/"
CLIENT_SECRETS_FILE = DIR_+"client_secret.json"

SCOPES = ["https://mail.google.com/"]
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

@jwt_required
@bp.route('/getmail', methods=["POST", "GET"])
def getMail():
	data = request.get_json()
	ID = data['studentId']
	if not os.path.exists(DIR_+'tokens/'+ID+'.json'):
		session["ID"] = ID
		return jsonify({'response': 'auth'})
	dir = DIR_+'messages/'+ID+'.json'
	if os.path.exists(dir):
		jsonMsg = open(dir).read()
		messages = json.loads(jsonMsg)
	else:
		print('\ndoesnt exist\n')
		print("\nvisited:",data["visited"], "\n")
		if data["visited"] == False:
			return jsonify({ "response": "first-time" })
		messages = []
	Gmail_ = Gmail(token=ID)
	unsavedMessages = Gmail_.getUserInfo()['messagesTotal'] - len(messages)
	# print("\nUnsaved Messages", unsavedMessages, "\n")
	# if unsavedMessages > 100:
	# 	unsavedMessages = 100
	if unsavedMessages > 0:
		messages_ = GetMessages(token=ID).list(unsavedMessages)
		messageData = Gmail_.getMessageData(messages_, log=False)
		payloads = Gmail_.getPayload(messageData, log=False)
		parts = Gmail_.unpackPayload(payloads, log=False)
		messages = messages+parts
	debug.writeLog(ID, messages, directory="messages/", cwd=DIR_[:-1])
	if len(messages) > 50:
		return jsonify(messages[:50])
	return jsonify(messages)

@bp.route("/gettoken", methods=["POST", "GET"])
def getToken():
	credentials = google.oauth2.credentials.Credentials(
		**session['credentials'])
	print('\nCredentials ===========================')
	for attr, value in credentials.__dict__.items():
		print('\t',attr, value)
	print('=========================== Credentials\n')
	cred = credentials_to_dict(credentials)
	a = open(DIR_+'token_.json').read()
	b = json.loads(a)
	for key, val in cred.items():
		if key == 'token':
			b['access_token'] = val
			b["token_response"]["access_token"] = val
		else:
			b[key] = val
	ID = session["ID"]
	print("\n__ID__", ID, "\n")
	a = open(DIR_+'tokens/'+ID+'.json', 'w')
	json.dump(b, a)
	session['credentials'] = cred
	return redirect("http://localhost:3000/teacher/classroom/email")

@bp.route('/authorize', methods=["GET", "POST"])
def authorize():
	# print('\n', os.path.exists("app/controllers/email/client_secret.json"), "\n")
	userId = flask.request.args.get("id")
	session["ID"] = userId
	print("UserId is " + userId)
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
		CLIENT_SECRETS_FILE, scopes=SCOPES)
	flow.redirect_uri = url_for('email.oauth2callback', _external=True)
	authorization_url, state = flow.authorization_url(
										access_type='offline')
	session['state'] = state
	return redirect(authorization_url)

@bp.route('/oauth2callback', methods=["POST", "GET"])
def oauth2callback():
	state = session['state']
	# print('\n\at oauth2Callback\n')
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
		CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
	flow.redirect_uri = url_for('email.oauth2callback', _external=True)
	authorization_response = request.url
	flow.fetch_token(authorization_response=authorization_response)
	credentials = flow.credentials
	session['credentials'] = credentials_to_dict(credentials)
	return redirect(url_for('email.getToken'))

@bp.route('/clear')
def clear_credentials():
	if 'credentials' in session:
		del session['credentials']
	return 'Credentials have been cleared.'

def credentials_to_dict(credentials):
	return {'token': credentials.token,
				'refresh_token': credentials.refresh_token,
				'token_uri': credentials.token_uri,
				'client_id': credentials.client_id,
				'client_secret': credentials.client_secret,
				}
