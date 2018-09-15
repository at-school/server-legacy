from datetime import datetime

import graphene
import pymongo
from bson.objectid import ObjectId
from flask import request
from flask_jwt_extended import get_jwt_identity
from graphql import GraphQLError

from app.database import db
from app.graphql.schemas.chatroom import ChatroomSchema
from app.graphql.schemas.classroom import ClassroomSchema
from app.graphql.schemas.message import MessageSchema
from app.graphql.schemas.schedule import ScheduleSchema
from app.graphql.schemas.user import UserSchema
from app.models import User

from app.graphql.inputs.schedule import ScheduleInput
from app.graphql.inputs.user import UserInput
from app.graphql.inputs.classroom import ClassroomInput

from app.graphql.inputs.message import MessageInput
from app.graphql.inputs.chatroom import ChatroomInput

from app.graphql.mutations.createUser import CreateUser
from app.graphql.mutations.createClassroom import CreateClassroom
from app.graphql.mutations.removeClassroom import RemoveClassroom
from app.graphql.mutations.editClassroom import EditClassroom
from app.graphql.mutations.createChatRoom import CreateChatroom
from app.graphql.mutations.createMessage import CreateMessage
from app.graphql.mutations.addStudentToClassroom import AddStudentToClassroom
from app.graphql.mutations.removeStudentFromClassroom import RemoveStudentFromClassroom

class Mutation(graphene.ObjectType):
    createUser = CreateUser.Field()
    createClassroom = CreateClassroom.Field()
    removeClassroom = RemoveClassroom.Field()
    editClassroom = EditClassroom.Field()
    createChatroom = CreateChatroom.Field()
    createMessage = CreateMessage.Field()
    addStudentToClassroom = AddStudentToClassroom.Field()
    removeStudentFromClassroom = RemoveStudentFromClassroom.Field()


class Query(graphene.ObjectType):
    user = graphene.List(UserSchema, arguments=UserInput(required=True))
    classroom = graphene.List(
        ClassroomSchema, arguments=ClassroomInput(required=True))
    chatroom = graphene.List(
        ChatroomSchema, arguments=ChatroomInput(required=True))
    message = graphene.List(
        MessageSchema, arguments=MessageInput(required=True))
    schedule = graphene.List(
        ScheduleSchema, arguments=ScheduleInput(required=True))

    def resolve_user(self, info, arguments):
        users = None
        if arguments.get("_id", None):
            users = list(db.users.find({"_id": ObjectId(arguments["_id"])}))
        else:
            users = list(db.users.find(arguments))
        print(users)
        return map(lambda i: UserSchema(**i), users)

    def resolve_classroom(self, info, arguments):
        if arguments.get("_id", None):
            arguments["_id"] = ObjectId(arguments["_id"])
        classrooms = list(db.classrooms.find(arguments))
        return map(lambda i: ClassroomSchema(**i), classrooms)

    def resolve_chatroom(self, info, arguments):
        chatrooms = list(db.chatrooms.find(
            {"_id": ObjectId(arguments["_id"])}))
        print(chatrooms)
        return map(lambda room: ChatroomSchema(_id=room["_id"], name=room["name"]), chatrooms)

    def resolve_message(self, info, arguments):
        chatroomId = arguments.get("chatroomId", None)

        if chatroomId:
            messages = list(db.messages.find({"chatroomId": chatroomId}))
            return map(lambda message: MessageSchema(**message), messages)

    def resolve_schedule(self, info, arguments):
        schedule = list(db.schedule.find(arguments))

        return map(lambda s: ScheduleSchema(**s), schedule)


schema = graphene.Schema(query=Query, mutation=Mutation)
