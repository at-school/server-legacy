from __future__ import print_function

import ast
import base64
import hashlib
import hmac
import json
import os
from flask_jwt_extended import get_jwt_identity

import flask
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import requests
from bson.objectid import ObjectId
from flask import Flask, jsonify, redirect, request, session, url_for
from flask_jwt_extended import jwt_required
from googleapiclient.discovery import build
from httplib2 import Http

from app.controllers.email import bp
from app.controllers.email.authentication import auth
from app.controllers.email.MailLogging import debug
from app.controllers.email.PyMail import GetMessages, Gmail
from app.database import db

from ... import socketio

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
        if data["visited"] == False:
            return jsonify({"response": "first-time"})
        messages = []

    if not (os.path.exists(DIR_+'messages/'+ID+'.json')):
        Gmail_ = Gmail(token=ID, pushNotification=False)
        messages_ = GetMessages(token=ID).list(4)
        messageData = Gmail_.getMessageData(messages_, log=False)
        historyId = messageData[0]["historyId"]
        db.emails.update({"userId": ID}, {"userId": ID,
                                          "historyId": historyId}, upsert=True)
        payloads = Gmail_.getPayload(messageData, log=False)
        parts = Gmail_.unpackPayload(payloads, log=False)
        messages = messages + parts
        with open(os.path.dirname(__file__) + "/messages/" + ID + '.json', 'w') as outfile:
            json.dump(messages, outfile)
    else:
        gmail = Gmail(token=ID, pushNotification=False)
        historyId = db.emails.find_one(
            {"userId": ID}, {"historyId": 1}).get("historyId")
        historyInstance = gmail.getNewestEmail(historyId=historyId)
        mails = historyInstance.get("history", [])

        if len(mails) > 0:
            newestHistoryId = mails[0].get("historyId")
            if newestHistoryId:
                db.emails.update({"userId": ID}, {
                    "userId": ID, "historyId": newestHistoryId}, upsert=True)

        messages = []
        with open(os.path.dirname(__file__) + "/messages/" + ID + '.json') as f:
            messages = json.load(f)
        messagesIds = [message["Id"] for message in messages]
        for message in mails:
            messageInstances = message["messagesAdded"]

            messagesContent = [gmail.getSingleEmail(
                mailId=messageInstance["message"]["id"]) for messageInstance in messageInstances]

            print("this second email")
            messageData = gmail.getMessageData(
                dict(messages=messagesContent), log=False)
            payloads = gmail.getPayload(messageData, log=False)
            parts = gmail.unpackPayload(payloads, log=False)
            parts = [part for part in parts if part["Id"] not in messagesIds]
            messages = parts + messages

            with open(os.path.dirname(__file__) + "/messages/" + ID + '.json', 'w') as outfile:
                json.dump(messages, outfile)
        return jsonify(messages)
    return jsonify(messages)


@bp.route("/sendmail", methods=["POST"])
@jwt_required
def sendMail():
    data = request.get_json()
    print(data)
    gmail = Gmail(token=get_jwt_identity())
    if data.get("email"):
        gmail.sendMessage(data["email"],
                          data["subject"], data["mailData"])
    return jsonify({})


@bp.route("/", methods=["POST", "GET"])
def mainView():
    if request.method == "POST":
        data = request.get_json()
        decoded_data = ast.literal_eval(base64.urlsafe_b64decode(
            data["message"]["data"]).decode("ascii"))
        emailAddress = decoded_data["emailAddress"]
        usersIds = [str(user.get("_id", "")) for user in list(db.users.find(
            {"loginedEmail": emailAddress}, {"_id": 1}))]

        for userId in usersIds:
            socketio.emit("email", room=userId)

        return jsonify({})

    return "sdfsf"


@bp.route("/gettoken", methods=["POST", "GET"])
def getToken():
    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])
    print('\nCredentials ===========================')
    for attr, value in credentials.__dict__.items():
        print('\t', attr, value)
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
    a.close()
    session['credentials'] = cred

    userId = session["ID"]
    service = auth(userId)
    userProfile = service.users().getProfile(userId="me").execute()
    userEmailAddress = userProfile["emailAddress"]
    db.users.update({"_id": ObjectId(userId)}, {
        "$push": {"loginedEmail": userEmailAddress}})

    return redirect("http://localhost:3000/teacher/email")


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
