from datetime import datetime

import graphene
from graphql import GraphQLError
from bson.objectid import ObjectId
from flask_jwt_extended import get_jwt_identity

from app.database import db
from app.graphql.inputs.message import MessageInput
from app.graphql.schemas.message import MessageSchema


class CreateMessage(graphene.Mutation):
    class Arguments:
        arguments = MessageInput(required=True)

    Output = MessageSchema

    def mutate(self, info, arguments):
        if not arguments["senderAvatar"]:
            return GraphQLError("Do not have avatar")
        timestamp = datetime.utcnow()

        inserted_id = db.messages.insert_one(
            {
                "messageContent": arguments["messageContent"],
                "chatroomId": arguments["chatroomId"],
                "senderId": get_jwt_identity(),
                "timestamp": timestamp,
                "senderAvatar": arguments["senderAvatar"]
            }
        ).inserted_id

        db.chatrooms.update_one({"_id": ObjectId(arguments["chatroomId"])}, {"$set": {
            "timestamp": timestamp
        }}, upsert=True)

        return MessageSchema(messageContent=arguments["messageContent"],
                             _id=inserted_id, senderId=get_jwt_identity(),
                             timestamp=timestamp, senderAvatar=arguments["senderAvatar"])
