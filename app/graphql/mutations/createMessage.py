from datetime import datetime

import graphene
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
        timestamp = datetime.utcnow()

        # get the sender avatar and id
        senderUsername = get_jwt_identity()
        sender = db.users.find_one({"username": senderUsername})
        senderId = str(sender["_id"])
        senderAvatar = sender["avatar"]

        inserted_id = db.messages.insert_one(
            {
                "messageContent": arguments["messageContent"],
                "chatroomId": arguments["chatroomId"],
                "senderId": senderId,
                "timestamp": timestamp,
                "senderAvatar": senderAvatar
            }
        ).inserted_id

        db.chatrooms.update_one({"_id": ObjectId(arguments["chatroomId"])}, {"$set": {
            "timestamp": timestamp
        }}, upsert=True)

        return MessageSchema(messageContent=arguments["messageContent"],
                             _id=inserted_id, senderId=senderId,
                             timestamp=timestamp, senderAvatar=senderAvatar)
