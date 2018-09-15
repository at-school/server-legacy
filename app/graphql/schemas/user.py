import graphene
import pymongo
from bson.objectid import ObjectId

from app.database import db


class UserSchema(graphene.ObjectType):
    username = graphene.String()
    firstname = graphene.String()
    lastname = graphene.String()
    password = graphene.String()
    accessLevel = graphene.Int()
    email = graphene.String()
    avatar = graphene.String()
    faceEncoding = graphene.String()
    classrooms = graphene.List(lambda: ClassroomSchema)
    chatrooms = graphene.List(lambda: ChatroomSchema)
    latestChatroom = graphene.List(lambda: ChatroomSchema)
    studentClassroom = graphene.List(lambda: ClassroomSchema)
    _id = graphene.ID()

    def resolve_classrooms(self, info):
        classrooms = list(db.classrooms.find(
            {"teacherUsername": self.username}))
        return map(lambda i: ClassroomSchema(**i), classrooms)

    def resolve_chatrooms(self, info):
        chatrooms = list(db.chatrooms.find({}).sort(
            'timestamp', pymongo.DESCENDING))
        returnedChatrooms = []

        for room in chatrooms:
            if str(ObjectId(self._id)) in room["users"]:
                returnedChatrooms.append(room)

        return map(lambda room: ChatroomSchema(_id=room["_id"], name=room["name"]), returnedChatrooms)

    def resolve_latestChatroom(self, info):
        chatrooms = list(db.chatrooms.find({}).sort(
            'timestamp', pymongo.DESCENDING))
        returnedChatrooms = []

        for room in chatrooms:
            if str(ObjectId(self._id)) in room["users"]:
                returnedChatrooms.append(room)
                break

        return map(lambda room: ChatroomSchema(_id=room["_id"], name=room["name"]), returnedChatrooms)


from app.graphql.schemas.chatroom import ChatroomSchema
from app.graphql.schemas.classroom import ClassroomSchema

