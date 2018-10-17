from bson.objectid import ObjectId
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_socketio import close_room, emit, join_room, leave_room, send

from app.controllers.errors import bad_request
from app.controllers.users import bp
from app.database import db
from app.decorators import teacher_required

from ... import socketio
import oauth2client


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


@bp.route("/user/info", methods=["POST"])
@jwt_required
def getUserInfo():
    try:
        user = db.users.find_one({"_id": ObjectId(get_jwt_identity())})

        return jsonify({"email": user["email"], "phone": user["phone"], "firstname": user["firstname"], "lastname": user["lastname"], "avatar": user["avatar"]})

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
        print("User " + get_jwt_identity() + " connected")

        # notify all the room that user just goes online
        db.users.update({'_id': ObjectId(get_jwt_identity())}, {
                        "$set": {"active": True}}, upsert=False)
        emit("userOnline", {"newUserId": userIdentity},
             room="userStatus:" + get_jwt_identity())

    if activityType == "deleteChatroom":
        otherUser = data["otherUser"]
        chatroomId = data["chatroomId"]
        print("Notify to delete %s from %s" % (chatroomId, otherUser))
        emit("deleteChatroom", {"chatroomId": chatroomId}, room=otherUser)

    if activityType == "createChatroom":
        otherUser = data["otherUser"]
        createChatroom = data["createChatroom"]

        emit("createChatroom", {
             "createChatroom": createChatroom}, room=otherUser)

    if activityType == "joinUserStatus":
        users = data["users"]
        for user in users:
            join_room("userStatus:" + user)

        return False

    if activityType == "leaveUserStatus":
        leave_room(get_jwt_identity())
        return False


@socketio.on('disconnect', namespace='/user')
@jwt_required
def test_disconnect():
    db.users.update({'_id': ObjectId(get_jwt_identity())}, {
                    "$set": {"active": False}}, upsert=False)
    print("User " + get_jwt_identity() + " disconnected")
    emit("userOffline", {"leaveUserId": get_jwt_identity()},
         room="userStatus:" + get_jwt_identity())
