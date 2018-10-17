import jwt
from bson.objectid import ObjectId
from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_socketio import emit, join_room, leave_room, send

from app.controllers.messaging.queries import *
from app.database import db
from app.graphql import schema

from ... import socketio


@socketio.on('sendMessage', namespace='/message')
@jwt_required
def join(data):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""

    # get activity type and user id
    activityType = data["activityType"]

    if activityType == "join":
        join_room(data['chatroomId'])

    if activityType == "newMessage":

        # append message to the message table
        # schema.execute(createMessageQuery(message, room))

        emit('newMessage', {
            "createMessage": data["createMessage"],
            "chatroomId": data["chatroomId"]
        }, room=data["chatroomId"])
