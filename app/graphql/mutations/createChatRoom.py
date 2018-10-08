from datetime import datetime

import graphene
from flask_jwt_extended import get_jwt_identity
from graphql import GraphQLError

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
        name = arguments["name"]

        if not firstId:
            return GraphQLError("Missing firstId")
        elif not secondId:
            return GraphQLError("Missing secondId")
        elif not name:
            return GraphQLError("Missing name")

        timestamp = datetime.utcnow()

        inserted_id = db.chatrooms.insert_one({
            "users": [firstId, secondId],
            "timestamp": timestamp,
            "name": name,
        }).inserted_id

        return ChatroomSchema(_id=inserted_id, timestamp=timestamp, name=name)
