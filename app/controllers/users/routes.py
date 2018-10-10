from bson.objectid import ObjectId
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_socketio import close_room, emit, join_room, leave_room, send

from app.controllers.errors import bad_request
from app.controllers.users import bp
from app.database import db
from app.decorators import teacher_required

from ... import socketio


@jwt_required
@bp.route("/user/search", methods=["POST"])
def searchUser():
    try:
        data = request.get_json()
        searchPattern = data["searchPattern"]
        users = list(db.users.find({"username": {"$regex": searchPattern}}))
        users = list(map(lambda user: {"_id": str(
            user["_id"]), "firstname": user["firstname"], "lastname": user["lastname"], "avatar": user["avatar"]}, users))
        print(users)
        return jsonify({"data": users})
    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")


@jwt_required
@teacher_required
@bp.route("/user/search/student", methods=["POST"])
def searchStudent():
    try:
        data = request.get_json()
        searchPattern = data["searchPattern"]
        users = list(db.users.find(
            {"username": {"$regex": searchPattern}, "accessLevel": 1}))
        users = list(map(lambda user: {"Id": str(
            user["_id"]), "name": user["firstname"] + " " + user["lastname"], "avatar": user["avatar"]}, users))
        print(users)
        return jsonify({"data": users})
    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")


@bp.route("/user/edit/bio", methods=["POST"])
@jwt_required
def editBio():
    try:
        data = request.get_json()
        userId = data["userId"]
        bio = data["bio"]

        db.users.update_one({"_id": ObjectId(userId)}, {"$set": {"bio": bio}})

        return jsonify({"bio": bio})

    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")


@socketio.on('user', namespace='/user')
@jwt_required
def active_time(data):
    """
    Track the activity of the user
    activeType:
        - join: user joining a room
        - create: user opening a room (socket connection)
    userId: the id of the user
    """
    activityType = data["activityType"]

    if activityType == "join":
        userIdentity = data["userIdentity"]
        join_room(userIdentity)
        return False

    if activityType == "deleteChatroom":
        otherUser = data["otherUser"]
        chatroomId = data["chatroomId"]
        print("Notify to delete %s from %s" % (chatroomId, otherUser))
        emit("deleteChatroom", {"chatroomId": chatroomId}, room=otherUser)

    if activityType == "createChatroom":
        otherUser = data["otherUser"]
        createChatroom = data["createChatroom"]
        print("New created chatroom: ", end="")
        print(createChatroom)
        print("From id" + otherUser)
        emit("createChatroom", {
             "createChatroom": createChatroom}, room=otherUser)


@socketio.on('disconnect', namespace='/activetime')
def test_disconnect():
    pass
