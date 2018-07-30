import jwt
from flask import request, jsonify, current_app, redirect, url_for
from app.controllers.auth import bp
from app.models import User
from app import db
from app.controllers.errors import bad_request

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
@bp.route("/auth/signin", methods=["POST"])
def signin():
    try:
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        user = User.query.filter_by(username=username).first()
        if not user:
            return bad_request("Incorrect username or password.")
        if user and user.check_password(password):
            public_key = open(current_app.config["JWT_KEY_PUBLIC"]).read()
            private_key = open(current_app.config["JWT_KEY_PRIVATE"]).read()
            token = jwt.encode({
                "id": user.id,
                "username": username,
            }, private_key, algorithm="RS256").decode("utf-8")
            user.login(token)
            fullname = user.firstname + " " + user.lastname
            return jsonify({
                "token": token, 
                "avatarUrl": user.get_default_avatar(256), 
                "userType": user.access_level,
                "fullname": fullname
                })
    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")

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
        payload = jwt.decode(token, open(current_app.config["JWT_KEY_PUBLIC"]).read(), algorithms=['RS256'])
        user = User.query.filter_by(id=payload["id"]).first()
        user.logout()
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
        username = data["username"]
        password = data["password"]
        password1 = data["password1"]
        firstname = data["firstname"]
        lastname = data["lastname"]
        email = data["email"]
        access_level = data["accessLevel"]

        if access_level not in ["1", "2", 1, 2]:
            return bad_request("Type is not correct.")

        if (password != password1 or len(password) < 8 or not firstname 
            or not lastname or not email or not username):
            return bad_request("Please check in with all the fields.")

        user = User.query.filter_by(username=username).first()
        if (user):
            return bad_request("Username already exists.")
        
        # when passed all the validations, add user in the database
        user = User(username=username, email=email, firstname=firstname, lastname=lastname, access_level=int(access_level))
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

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

        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({"duplicate": True})
        

        return jsonify({"duplicate": False})
    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")
