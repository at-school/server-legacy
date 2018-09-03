from datetime import datetime

import graphene
import pymongo
from bson.objectid import ObjectId
from flask import request
from flask_jwt_extended import get_jwt_identity
from graphql import GraphQLError

from app.database import db
from app.models import User


class UserSchema(graphene.ObjectType):
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


class ScheduleSchema(graphene.ObjectType):
    _id = graphene.ID()
    line = graphene.String()
    day = graphene.String()
    startTime = graphene.String()
    endTime = graphene.String()


class ScheduleInput(graphene.InputObjectType):
    _id = graphene.ID()
    line = graphene.String()
    day = graphene.String()
    startTime = graphene.String()
    endTime = graphene.String()


class UserInput(graphene.InputObjectType):
    username = graphene.String()
    firstname = graphene.String()
    lastname = graphene.String()
    password = graphene.String()
    accessLevel = graphene.Int()
    email = graphene.String()


class ClassroomSchema(graphene.ObjectType):
    _id = graphene.ID()
    name = graphene.String()
    description = graphene.String()
    avatar = graphene.String()
    teacherUsername = graphene.String()
    lineId = graphene.String()
    falcutyId = graphene.String()


class ClassroomInput(graphene.InputObjectType):
    _id = graphene.ID()
    name = graphene.String()
    description = graphene.String()
    avatar = graphene.String()
    teacherUsername = graphene.String()
    lineId = graphene.String()
    falcutyId = graphene.String()


class MessageInput(graphene.InputObjectType):
    chatroomId = graphene.ID()
    messageContent = graphene.String()
    senderId = graphene.ID()
    senderAvatar = graphene.String()


class MessageSchema(graphene.ObjectType):
    _id = graphene.ID()
    senderId = graphene.ID()
    senderAvatar = graphene.String()
    messageContent = graphene.String()
    timestamp = graphene.DateTime()
    chatroomId = graphene.ID()


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


class ChatroomSchema(graphene.ObjectType):
    _id = graphene.ID()
    users = graphene.List(UserSchema)
    messages = graphene.List(MessageSchema)
    timestamp = graphene.DateTime()
    name = graphene.String()
    latestMessage = graphene.List(MessageSchema)

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
            {"_id": ObjectId(id)}), userIds)

        return map(lambda userInfo: UserSchema(**userInfo), users)

    def resolve_latestMessage(self, info):
        messages = list(db.messages.find({"chatroomId": str(self._id)}).sort(
            'timestamp', pymongo.DESCENDING).limit(1))
        return map(lambda message: MessageSchema(**message), messages)


class ChatroomInput(graphene.InputObjectType):
    _id = graphene.ID()
    firstId = graphene.ID()
    secondId = graphene.ID()


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
        users = list(db.users.find(arguments))
        return map(lambda i: UserSchema(**i), users)

    def resolve_classroom(self, info, arguments):
        if arguments.get("_id", None):
            arguments["_id"] = ObjectId(arguments["_id"])
        if not arguments.get("teacherUsername", None):
            arguments["teacherUsername"] = get_jwt_identity()
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


class CreateUser(graphene.Mutation):
    class Arguments:
        arguments = UserInput(required=True)

    Output = UserSchema

    def mutate(self, info, arguments):
        u = User(**arguments)
        u.setPassword(arguments.password)
        db.users.insert_one({
            "username": u.username,
            "password": u.password,
            "firstname": u.firstname,
            "lastname": u.lastname,
            "email": u.email,
            "accessLevel": u.accessLevel,
            "avatar": u.avatar
        })
        return UserSchema(**arguments, avatar=u.avatar)


class CreateClassroom(graphene.Mutation):
    class Arguments:
        arguments = ClassroomInput(required=True)

    Output = ClassroomSchema

    def mutate(self, info, arguments):
        arguments["teacherUsername"] = get_jwt_identity()
        db.classrooms.insert_one(arguments)
        return ClassroomSchema(**arguments)


class RemoveClassroomInput(graphene.InputObjectType):
    _id = graphene.ID()


class RemoveClassroom(graphene.Mutation):
    class Arguments:
        arguments = RemoveClassroomInput(required=True)

    Output = ClassroomSchema

    def mutate(self, info, arguments):
        print(arguments)
        if not arguments["_id"]:
            raise GraphQLError("Not the right query")
        db.classrooms.remove(ObjectId(arguments["_id"]))
        return ClassroomSchema(**arguments)


class EditClassroom(graphene.Mutation):
    class Arguments:
        arguments = ClassroomInput(required=True)

    Output = ClassroomSchema

    def mutate(self, info, arguments):
        db.classrooms.update_one({"_id": ObjectId(arguments["_id"])}, {"$set": {
            "name": arguments["name"],
            "description": arguments["description"],
            "avatar": arguments["avatar"],
            "lineId": arguments["lineId"],
            "falcutyId": arguments["falcutyId"]
        }}, upsert=True)
        return ClassroomSchema(**arguments)


class Mutation(graphene.ObjectType):
    createUser = CreateUser.Field()
    createClassroom = CreateClassroom.Field()
    removeClassroom = RemoveClassroom.Field()
    editClassroom = EditClassroom.Field()
    createChatroom = CreateChatroom.Field()
    createMessage = CreateMessage.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
