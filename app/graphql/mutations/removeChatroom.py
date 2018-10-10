from datetime import datetime

import graphene
from bson.objectid import ObjectId
from graphql import GraphQLError

from app.database import db
from app.graphql.inputs.chatroom import ChatroomInput
from app.graphql.schemas.chatroom import ChatroomSchema


class RemoveChatroom(graphene.Mutation):
    class Arguments:
        arguments = ChatroomInput(required=True)

    Output = ChatroomSchema

    def mutate(self, info, arguments):
        # get the id of the room
        if not arguments["_id"]:
            return GraphQLError("Missing id of the room")

        db.chatrooms.delete_one({"_id": ObjectId(arguments["_id"])})
        db.messages.delete_many({"chatroomId": arguments["_id"]})

        return ChatroomSchema(_id=arguments["_id"])
