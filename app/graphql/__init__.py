from datetime import datetime

import graphene
import pymongo
from bson.objectid import ObjectId
from flask import request
from flask_jwt_extended import get_jwt_identity
from graphql import GraphQLError
from datetime import datetime, timedelta
from calendar import day_name


from app.database import db
from app.graphql.schemas.chatroom import ChatroomSchema
from app.graphql.schemas.classroom import ClassroomSchema
from app.graphql.schemas.message import MessageSchema
from app.graphql.schemas.schedule import ScheduleSchema
from app.graphql.schemas.user import UserSchema
from app.graphql.schemas.scheduleDetails import ScheduleDetailsSchema
from app.graphql.schemas.latestLine import LatestLineSchema
from app.models import User

from app.graphql.inputs.schedule import ScheduleInput
from app.graphql.inputs.user import UserInput
from app.graphql.inputs.classroom import ClassroomInput

from app.graphql.inputs.message import MessageInput
from app.graphql.inputs.chatroom import ChatroomInput
from app.graphql.inputs.scheduleDetails import ScheduleDetailsInput

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
    scheduleDetails = graphene.Field(
        ScheduleDetailsSchema, arguments=ScheduleDetailsInput(required=True))
    latestLine = graphene.Field(LatestLineSchema)

    def resolve_user(self, info, arguments):
        users = None
        if arguments.get("_id", None):
            users = list(db.users.find({"_id": ObjectId(arguments["_id"])}))
        else:
            users = list(db.users.find(arguments))
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

    def resolve_scheduleDetails(self, info, arguments):

        def isInSchedule(scheduleList):
            if not scheduleList:
                return False

            latestSchedule = scheduleList[0]

            startTime = datetime.strptime(
                latestSchedule["startTime"], "%Y-%m-%d %H:%M:%S")
            endTime = datetime.strptime(
                latestSchedule["endTime"], "%Y-%m-%d %H:%M:%S")
            currentTime = datetime.now()
            # if the current time is before the latest shedule
            if currentTime < startTime:
                return True
            elif currentTime > startTime and currentTime < endTime:
                return True
            return False

        def getLine(line):
            day = datetime.now().weekday()
            counter = 0
            while True:
                currentLine = db.schedule.find_one(
                    {"line": line, "day": day_name[(day + counter) % 7]})
                print(currentLine)

                if currentLine:
                    currentTime = datetime.now() + timedelta(days=counter)
                    startHour, startMinute, startSecond = map(
                        int, currentLine["startTime"].split(":"))
                    finishHour, finishMinute, finishSecond = map(
                        int, currentLine["endTime"].split(":"))
                    startTime = datetime(currentTime.year, currentTime.month,
                                         currentTime.day, startHour, startMinute, startSecond)
                    finishTime = datetime(currentTime.year, currentTime.month,
                                          currentTime.day, finishHour, finishMinute, finishSecond)
                    if not (datetime.now() > finishTime):
                        return {
                            "line": line,
                            "startTime": startTime,
                            "endTime": finishTime
                        }


                counter += 1
                if (counter > 8):
                    break

        # check if the current time is in the latest schedule details
        latestLine = list(db.scheduleDetails.find({"line": arguments["line"], "classId": arguments["classId"]}, {"startTime": 1, "endTime": 1}).sort(
            'startTime', pymongo.DESCENDING).limit(1))

        if isInSchedule(latestLine):
            # do something here
            latestLine = latestLine[0]
            return ScheduleDetailsSchema(_id=str(latestLine["_id"]),
                                          line=str(arguments["line"]),
                                          startTime=str(
                latestLine["startTime"]),
                endTime=str(latestLine["endTime"]),
                classId=str(arguments["classId"]))
        else:
            # get the start time and end time of the line
            print("Here")
            lineData = getLine(arguments["line"])
            print(lineData)
            studentList = db.classrooms.find_one(
                {"teacherUsername": arguments["teacherUsername"], "lineId": lineData["line"]}, {"students": 1})
            if not studentList:
                return None
            print("Here after student list")
            studentsWithMarking = list(map(lambda student: {
                "_id": student, "inClass": False}, studentList["students"]))
            print("Here after students with marking")

            scheduleToSave = {
                "line": lineData["line"],
                "students": studentsWithMarking,
                "startTime": str(lineData["startTime"]),
                "endTime": str(lineData["endTime"]),
                "classId": arguments["classId"]
            }

            inserted_id = db.scheduleDetails.insert_one(
                scheduleToSave).inserted_id

            return ScheduleDetailsSchema(_id=str(inserted_id),
                                          line=str(arguments["line"]),
                                          startTime=str(lineData["startTime"]),
                                          endTime=str(lineData["endTime"]),
                                          classId=str(arguments["classId"]))

        return []

    def resolve_latestLine(self, info):
        currentTime = datetime.now()
        currentDay = currentTime.weekday()
        counter = 0
        while True:
            updateTime = datetime.now() + timedelta(days=counter)
            schedule = list(db.schedule.find(
                {"day": day_name[(currentDay + counter) % 7]}))
            if not schedule:
                print("does not have any schedule")
                counter += 1
                continue

            # check if right now is the beginning
            firstLine = schedule[0]
            startHour, startMinute, startSecond = map(
                int, firstLine["startTime"].split(":"))
            startTime = datetime(updateTime.year, updateTime.month,
                                 updateTime.day, startHour, startMinute, startSecond)

            lastLine = schedule[-1]
            endHour, endMinute, endSecond = map(
                int, lastLine["endTime"].split(":"))
            endTime = datetime(updateTime.year, updateTime.month,
                               updateTime.day, endHour, endMinute, endSecond)

            if currentTime < startTime:
                # do something when it is the beginning of class
                endHour, endMinute, endSecond = map(
                    int, firstLine["endTime"].split(":"))
                endTime = datetime(updateTime.year, updateTime.month,
                                   updateTime.day, endHour, endMinute, endSecond)
                return LatestLineSchema(_id=str(firstLine["_id"]), line=firstLine["line"], startTime=str(startTime), endTime=str(endTime))
            elif currentTime > endTime:

                counter += 1
                continue
            else:
                for s in schedule:
                    startHour, startMinute, startSecond = map(
                        int, s["startTime"].split(":"))
                    endHour, endMinute, endSecond = map(
                        int, s["endTime"].split(":"))

                    startTime = datetime(currentTime.year, currentTime.month,
                                         currentTime.day, startHour, startMinute, startSecond)

                    endTime = datetime(currentTime.year, currentTime.month,
                                       currentTime.day, endHour, endMinute, endSecond)
                    if currentTime >= startTime and currentTime <= endTime:
                        return LatestLineSchema(_id=str(s["_id"]), line=s["line"], startTime=str(startTime), endTime=str(endTime))

            counter += 1


schema = graphene.Schema(query=Query, mutation=Mutation)
