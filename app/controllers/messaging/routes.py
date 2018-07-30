import jwt
from flask import request, jsonify, current_app
from flask_socketio import join_room, leave_room, emit, send
from ... import socketio
from app import db
from app.controllers.messaging import bp
from app.models import User, Message, ChatRoom
from config import Config
from app.controllers.errors import bad_request
from sqlalchemy import and_, or_

"""
Get all the rooms of a certain users
Arguments:
    - token: access token of the user
Returns:
    - a list of room containing all available messages
"""
@bp.route("/message/getrooms", methods=["POST"])
def get_rooms():
    # get user id
    data = request.get_json()
    payload = jwt.decode(data["token"], open(current_app.config["JWT_KEY_PUBLIC"]).read(), algorithms=['RS256'])
    user_id = payload["id"]

    user = User.query.filter_by(id=user_id).first()

    if not user: 
        return bad_request("User does not exist.")
    
    rooms = chat_room = ChatRoom.query.filter(or_(ChatRoom.first_user==user.id, 
            ChatRoom.second_user==user.id)).order_by(ChatRoom.access_time.desc()).all()

    results = []
    for room in rooms:
        # get other user
        other_user = None
        if room.first_user == user_id:
            other_user = User.query.filter_by(id=room.second_user)
        elif room.second_user == user_id:
            other_user = User.query.filter_by(id=room.first_user)
        else: 
            other_user = User.query.filter_by(id=room.first_user)

        other_user = other_user.first()

        # get all messages of that room
        messages = Message.query.filter_by(chat_room=room.id).order_by(Message.timestamp.asc()).all()

        messages_json = []
        for message in messages:
            from_user = False
            if message.from_id == user_id:
                from_user = True
            
            sender = User.query.filter_by(id=message.from_id).first()

            messages_json.append({
                "self": from_user,
                "senderAvatar": sender.get_default_avatar(256),
                "content": message.content,
            })

        results.append({
            "id": room.id,
            "avatarData": other_user.get_default_avatar(256),
            "name": other_user.firstname + " " + other_user.lastname,
            "messages": messages_json
        })

    return jsonify({"results": results})



"""
Create a new chat room between a user and another user.
Arguments:
    - token: access token of the user
    - otherId: id of the other user
Returns:
    - true when succescfully creating
"""
@bp.route("/message/createroom", methods=["POST"])
def create_room():
    # get user id
    data = request.get_json()
    payload = jwt.decode(data["token"], open(current_app.config["JWT_KEY_PUBLIC"]).read(), algorithms=['RS256'])
    user_id = payload["id"]
    other_id = int(data["otherId"])

    print("Pass getting data from the request")

    user = User.query.filter_by(id=user_id).first()
    other_user = User.query.filter_by(id=other_id).first()

    print("Pass getting two users")

    if not user or not other_user: 
        return bad_request("User does not exist.")
    
    chat_room = ChatRoom.query.filter(
        or_(and_(ChatRoom.first_user==user.id, ChatRoom.second_user==other_user.id),
        and_(ChatRoom.first_user==other_user.id, ChatRoom.second_user==user.id))
    ).first()

    if chat_room:
        return bad_request("Room already exists.")

    new_room = ChatRoom(first_user=user.id, second_user=other_user.id)
    print(new_room)
    db.session.add(new_room)
    db.session.commit()

    return jsonify({})
  
"""
Search users by a pattern
Arguments:
    - id: id of the user
    - searchPattern: the search pattern
Returns:
    - A list of users containing id and name
"""
@bp.route("/message/search/users", methods=["POST"])
def search_users():
    try: 
        # get user id
        data = request.get_json()
        payload = jwt.decode(data["token"], open(current_app.config["JWT_KEY_PUBLIC"]).read(), algorithms=['RS256'])
        user_id = payload["id"]
        search_pattern = data["searchPattern"]

        user = User.query.filter_by(id=user_id).first()
        if not user: 
            return bad_request("User does not exist.")

        user_list = User.query.filter(User.firstname.like("%{}%".format(search_pattern)) 
                                    | User.lastname.like("%{}%".format(search_pattern))).all()

        results = []
        for u in user_list:
            results.append({
                "id": u.id,
                "name": u.firstname + " " + u.lastname
            })
        
        
        return jsonify({"results": results})
        
    except:
        return jsonify({})




@socketio.on('join', namespace='/message')
def join(data):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""

    # check if user exists
    payload = jwt.decode(data["token"], open(current_app.config["JWT_KEY_PUBLIC"]).read(), algorithms=['RS256'])
    user_id = payload["id"]

    user = User.query.filter_by(id=user_id).first()
    if not user: 
        return False
    
    room = data['room']
    
    # check if room exists
    temp_room = ChatRoom.query.filter_by(id=room).first()
    if not temp_room:
        return False
    
    # check if user is in that room
    if temp_room.first_user != user_id and temp_room.second_user != user_id:
        return False

    # get message and assign user into the room
    message = data.get("message", None)
    join_room(room)

    print(request.sid)
        
    # add new message record to message table
    if message:
        new_message = Message(from_id=user_id, content=message, chat_room=int(room))
        db.session.add(new_message)
        db.session.commit()
        emit('status', {
                "self": False,
                "senderAvatar": user.get_default_avatar(256),
                "content": message,
            }, room=room)
    



