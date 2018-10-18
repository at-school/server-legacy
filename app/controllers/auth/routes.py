from flask import current_app, jsonify, redirect, request, url_for
from flask_jwt_extended import (create_access_token, get_jwt_claims,
                                get_jwt_identity, jwt_required)

import app
from app import jwt
from app.controllers.auth import bp
from app.controllers.auth.queries import *
from app.controllers.errors import bad_request
from app.decorators import teacher_required, admin_required
from app.models import User
from app.graphql import schema
import os
from app.database import db
from datetime import datetime, timedelta
from hashlib import md5
from app.controllers.email.PyMail import Gmail


"""
Sign in an user
Arguments:
    - username: username of the user
    - password: password of the user
Returns upon success:
    - token: the access token for that user
    - avatarUrl: the url to the user avatar
    - userType: the access level of the user (1 for student and 2 for teacher)
    - fullname: fullname of the user
"""


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {'role': int(user.get("accessLevel")), "Id": str(user.get("_id"))}


@jwt.user_identity_loader
def user_identity_lookup(user):
    return str(user.get("Id", None))


@bp.route("/auth/signin", methods=["POST"])
def signin():
    try:
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        query = loginQuery(username)
        user = schema.execute(query, context_value={"accessLevel": 4})
        user = user.data.get("user")
        if user and len(user) != 1:
            return bad_request("Incorrect username or password.")
        user = user[0]
        if User.checkPassword(user.get("password", None), password):
            expires = timedelta(days=365)
            accessToken = create_access_token(
                identity=user, expires_delta=expires)
            print(os.path.abspath(__file__))
            gmail = Gmail(token=str(user.get("_id")))
            return jsonify({
                "token": accessToken,
                "username": user.get("username"),
                "userId": str(user.get("Id")),
                "avatarUrl": user.get("avatar"),
                "userType": user.get("accessLevel"),
                "fullname": user.get("firstname") + " " + user.get("lastname"),
                "accessLevel": user.get("accessLevel")
            })
    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")


@bp.route('/protected', methods=['GET'])
@teacher_required
def protected():
    ret = {
        'current_identity': get_jwt_identity(),  # test
        'current_roles': get_jwt_claims()  # ['foo', 'bar']
    }
    print(get_jwt_claims())
    print(get_jwt_identity())
    return jsonify(ret), 200


"""
Sign the user out.
Arguments:
    - token: access token of the user
Returns nothing upon success.
"""


@bp.route("/auth/signout", methods=["POST"])
def signout():
    try:
        data = request.get_json()
        token = data["token"]
        return jsonify({})
    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")


"""
Register the user
Arguments:
    - username: username of the user
    - password: password of the user
    - password1: re-type password of the user
    - firstname: firstname of the uesr
    - lastname: lastname of the uesr
    - email: email of the user
    - accessLevel: access level of the user (1 for student, 2 for teacher)
"""


@bp.route("/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        print(data)
        username = data["username"]
        password = data["password"]
        password1 = data["password1"]
        firstname = data["firstname"]
        lastname = data["lastname"]
        email = data["email"]
        accessLevel = data["accessLevel"]
        dob = data["dob"]
        gender = data["gender"]
        data["phone"] = data["prefix"] + data["phone"]

        if accessLevel not in ["1", "2", 1, 2]:
            return bad_request("Type is not correct.")

        if (password != password1 or len(password) < 8 or not firstname
                or not lastname or not email or not username):
            return bad_request("Please check in with all the fields.")

        user = schema.execute(loginQuery(username))
        if len(user.data.get("user")) != 0:
            return bad_request("User already exists.")

        u = User(**data)
        u.setPassword(data["password"])
        inserted_id = str(db.users.insert_one({
            "username": u.username,
            "password": u.password,
            "firstname": u.firstname,
            "lastname": u.lastname,
            "email": u.email,
            "accessLevel": u.accessLevel,
            "avatar": u.avatar,
            "gender": data["gender"],
            "dob": u.dob,
            "studentClassroom": [],
            "activities": [],
            "phone": data["phone"],

        }).inserted_id)
        timestamp = datetime.utcnow()
        inserted_id = str(db.chatrooms.insert_one({
            "users": [inserted_id],
            "timestamp": timestamp,
            "name": "Team @ School"
        }).inserted_id)
        avatar_digest = md5(
            "phamduyanh249@live.com".lower().encode('utf-8')).hexdigest()
        db.messages.insert_one(
            {
                "messageContent": "Hello, welcome to @ School!",
                "chatroomId": inserted_id,
                "senderId": "",
                "timestamp": timestamp,
                "senderAvatar": 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
                    avatar_digest, 512)
            }
        )

        return jsonify({})

    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")


"""
Check if a username is duplicated
Arguments:
    - username: string
Returns:
    - duplicate: false if not duplicated or else true
"""


@bp.route("/auth/duplicateuser", methods=["POST"])
def duplicate_user():
    try:
        data = request.get_json()
        username = data["username"]

        user = schema.execute(loginQuery(username))
        if len(user.data.get("user")) != 0:
            return jsonify({"duplicate": True})

        return jsonify({"duplicate": False})
    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")
