import graphene
from app.database import db
from bson.objectid import ObjectId
import pymongo


class ChatroomSchema(graphene.ObjectType):
    _id = graphene.ID()
    name = graphene.String()
    users = graphene.List(lambda: UserSchema)
    messages = graphene.List(lambda: MessageSchema)
    timestamp = graphene.DateTime()
    name = graphene.String()
    latestMessage = graphene.List(lambda: MessageSchema)
    

    def resolve_messages(self, info):
        messages = list(db.messages.find({"chatroomId": str(self._id)}))
        print(messages)
        return map(lambda message: MessageSchema(**message), messages)

    def resolve_users(self, info):
        # get the user IDs
        chatroom = db.chatrooms.find_one({"_id": ObjectId(self._id)})
        userIds = chatroom["users"]

        # get the user schema
        users = map(lambda id: db.users.find_one(
            {"_id": ObjectId(id)}, {"activities": 0}), userIds)

        return map(lambda userInfo: UserSchema(**userInfo), users)

    def resolve_latestMessage(self, info):
        messages = list(db.messages.find({"chatroomId": str(self._id)}).sort(
            'timestamp', pymongo.DESCENDING).limit(1))
        return map(lambda message: MessageSchema(**message), messages)

from app.graphql.schemas.message import MessageSchema
from app.graphql.schemas.user import UserSchema