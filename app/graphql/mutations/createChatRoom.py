from datetime import datetime

import graphene
from flask_jwt_extended import get_jwt_identity

from app.database import db
from app.graphql.inputs.chatroom import ChatroomInput
from app.graphql.schemas.chatroom import ChatroomSchema


class CreateChatroom(graphene.Mutation):
    class Arguments:
        arguments = ChatroomInput(required=True)

    Output = ChatroomSchema

    def mutate(self, info, arguments):
        # find the users based on the username and get the IDs from them
        firstId = arguments.get("firstId", None)
        secondId = arguments.get("secondId", None)

        # get the ID of the user
        username = get_jwt_identity()
        user = db.users.find_one({"username": username})
        userIdentity = str(user["_id"])

        if not firstId:
            firstId = userIdentity
        elif not secondId:
            secondId = userIdentity

        timestamp = datetime.utcnow()

        inserted_id = db.chatrooms.insert_one({
            "users": [firstId, secondId],
            "timestamp": timestamp,
            "name": username
        }).inserted_id

        return ChatroomSchema(_id=inserted_id, timestamp=timestamp, name=username)
