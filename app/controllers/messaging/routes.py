import jwt
from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_socketio import emit, join_room, leave_room, send

from app.controllers.messaging.queries import *
from app.database import db
from app.schema import schema

from ... import socketio

@socketio.on('sendMessage', namespace='/message')
@jwt_required
def join(data):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""

    # get the user id
    username = get_jwt_identity()

    if not username:
        return False

    user = db.users.find_one({"username": username})
    userId = user["_id"]

    if not user:
        return False

    message = data.get("message", None)

    room = data['room']
    join_room(room)

    if message:

        # append message to the message table
        schema.execute(createMessageQuery(message, room))
        print("Emitting back")
        emit('newMessage', {
            "roomId": room
        }, room=room)
