import os
import graphene
import pymongo
from bson.objectid import ObjectId

from app.database import db
from app.graphql.schemas.skill import SkillSchema


class UserSchema(graphene.ObjectType):
    _id = graphene.ID()
    username = graphene.String()
    firstname = graphene.String()
    lastname = graphene.String()
    password = graphene.String()
    accessLevel = graphene.Int()
    email = graphene.String()
    avatar = graphene.String()
    classrooms = graphene.List(lambda: ClassroomSchema)
    chatrooms = graphene.List(lambda: ChatroomSchema)
    latestChatroom = graphene.List(lambda: ChatroomSchema)
    studentClassroom = graphene.List(lambda: ClassroomSchema)
    skills = graphene.List(SkillSchema)
    bio = graphene.String()
    dob = graphene.String()
    gender = graphene.String()
    phone = graphene.String()
    active = graphene.Boolean()

    def resolve_classrooms(self, info):
        classrooms = list(db.classrooms.find(
            {"teacherUsername": self.username}))

        classrooms1 = []
        for classroom in classrooms:
            classroom_id = str(classroom["_id"])
            with open(os.path.join(os.getcwd(), "class_images", str(classroom_id) + ".txt"), 'r') as f:
                classroom["avatar"] = f.read()
                classrooms1.append(classroom)
        return map(lambda i: ClassroomSchema(**i), classrooms1)

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

    def resolve_skills(self, info):
        skills = list(db.skills.find({"userId": str(self._id)}))

        return [SkillSchema(**skill) for skill in skills]


from app.graphql.schemas.chatroom import ChatroomSchema
from app.graphql.schemas.classroom import ClassroomSchema
