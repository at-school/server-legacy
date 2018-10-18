from datetime import datetime

import os
import json
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
from app.graphql.schemas.rollmarkingActivities import RollMarkingActivitiesSchema
from app.graphql.schemas.email import EmailSchema
from app.models import User

from app.graphql.inputs.schedule import ScheduleInput
from app.graphql.inputs.user import UserInput
from app.graphql.inputs.classroom import ClassroomInput

from app.graphql.inputs.message import MessageInput
from app.graphql.inputs.chatroom import ChatroomInput
from app.graphql.inputs.scheduleDetails import ScheduleDetailsInput
from app.graphql.inputs.rollmarkingActivities import RollMarkingActivitiesInput
from app.graphql.inputs.email import EmailInput

from app.graphql.mutations.createUser import CreateUser
from app.graphql.mutations.createClassroom import CreateClassroom
from app.graphql.mutations.removeClassroom import RemoveClassroom
from app.graphql.mutations.editClassroom import EditClassroom
from app.graphql.mutations.createChatRoom import CreateChatroom
from app.graphql.mutations.removeChatroom import RemoveChatroom
from app.graphql.mutations.createMessage import CreateMessage
from app.graphql.mutations.addStudentToClassroom import AddStudentToClassroom
from app.graphql.mutations.removeStudentFromClassroom import RemoveStudentFromClassroom
from app.graphql.mutations.createSkill import CreateSkill
from app.graphql.mutations.removeSkill import RemoveSkill


class Mutation(graphene.ObjectType):
    createUser = CreateUser.Field()
    createClassroom = CreateClassroom.Field()
    removeClassroom = RemoveClassroom.Field()
    editClassroom = EditClassroom.Field()
    createChatroom = CreateChatroom.Field()
    createMessage = CreateMessage.Field()
    addStudentToClassroom = AddStudentToClassroom.Field()
    removeStudentFromClassroom = RemoveStudentFromClassroom.Field()
    createSkill = CreateSkill.Field()
    removeSkill = RemoveSkill.Field()
    removeChatroom = RemoveChatroom.Field()


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
    rollMarkingActivites = graphene.List(
        RollMarkingActivitiesSchema, arguments=RollMarkingActivitiesInput(required=True))
    email = graphene.List(EmailSchema, arguments=EmailInput(required=True))

    def resolve_user(self, info, arguments):
        users = None
        if arguments.get("_id", None):
            users = list(db.users.find(
                {"_id": ObjectId(arguments["_id"])}, {"activities": 0}))
        else:
            users = list(db.users.find(arguments, {"activities": 0}))

        return map(lambda i: UserSchema(**i), users)

    def resolve_email(self, info, arguments):
        print(arguments)
        if arguments["userId"]:
            current_path = os.path.join(
                os.getcwd(), "app", "controllers", "email", "messages", arguments["userId"] + ".json")
            try:
                with open(current_path, "r") as f:
                    messages = json.load(f)
                return [EmailSchema(dateTime=message["dateTime"],
                                    From=message.get("From", ""),
                                    FromEmail=message.get("From-email", ""),
                                    subject=message.get("subject", ""),
                                    html=message.get("html", ""),
                                    userId=arguments["userId"],
                                    _id=message["Id"]) for message in messages]
            except:
                print("In except")
            
        return []

    def resolve_classroom(self, info, arguments):
        if arguments.getdirname("_id", None):
            print(os.path.abspath(__file__))
            arguments["_id"]=ObjectId(arguments["_id"])
        classrooms=list(db.classrooms.find(arguments, {"avatar": 0}))

        classrooms1=[]
        for classroom in classrooms:
            classroom_id=str(classroom["_id"])
            with open(os.path.join(os.getcwd(), "class_images", str(classroom_id) + ".txt"), 'r') as f:
                classroom["avatar"]=f.read()
                classrooms1.append(classroom)
        print(classrooms1)
        return map(lambda i: ClassroomSchema(**i), classrooms1)

    def resolve_chatroom(self, info, arguments):
        chatrooms = list(db.chatrooms.find(
            {"_id": ObjectId(arguments["_id"])}))
        print(chatrooms)
        return map(lambda room: ChatroomSchema(_id=room["_id"], name=room["name"]), chatrooms)

    def resolve_message(self, info, arguments):
        chatroomId=arguments.get("chatroomId", None)

        if chatroomId:
            messages=list(db.messages.find({"chatroomId": chatroomId}))
            return map(lambda message: MessageSchema(**message), messages)

    def resolve_schedule(self, info, arguments):
        schedule=list(db.schedule.find(arguments))

        return map(lambda s: ScheduleSchema(**s), schedule)

    def resolve_scheduleDetails(self, info, arguments):

        if not arguments["classId"]:
            return GraphQLError("Missing class id")

        def isInSchedule(scheduleList):
            """
            Check if current time is in a certain timeframe
            """
            if not scheduleList:
                return False

            latestSchedule=scheduleList[0]

            startTime=latestSchedule["startTime"]
            endTime=latestSchedule["endTime"]
            currentTime=datetime.now()
            # if the current time is before the latest shedule
            if currentTime < startTime:
                return True
            elif currentTime > startTime and currentTime < endTime:
                return True
            return False

        def getLine(line):
            """
            Get current line.
            If there is no current line, get the next line
            """
            day=datetime.now().weekday()
            counter=0
            while True:
                currentLine=db.schedule.find_one(
                    {"line": line, "day": day_name[(day + counter) % 7]})
                print(currentLine)

                if currentLine:
                    currentTime=datetime.now() + timedelta(days = counter)
                    startHour, startMinute, startSecond=map(
                        int, currentLine["startTime"].split(":"))
                    finishHour, finishMinute, finishSecond=map(
                        int, currentLine["endTime"].split(":"))
                    startTime=datetime(currentTime.year, currentTime.month,
                                         currentTime.day, startHour, startMinute, startSecond)
                    finishTime=datetime(currentTime.year, currentTime.month,
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
                                         startTime=latestLine["startTime"],
                                         endTime=latestLine["endTime"],
                                         classId=str(arguments["classId"]))
        else:
            # get the start time and end time of the line
            lineData = getLine(arguments["line"])
            studentList = db.classrooms.find_one(
                {"teacherId": arguments["teacherId"], "lineId": lineData["line"]}, {"students": 1})
            if not studentList:
                return None
            studentsWithMarking = list(map(lambda student: dict(
                _id=student, inClass=False, minsLate=0), studentList["students"]))

            scheduleToSave = {
                "line": lineData["line"],
                "students": studentsWithMarking,
                "startTime": lineData["startTime"],
                "endTime": lineData["endTime"],
                "classId": arguments["classId"]
            }

            inserted_id = db.scheduleDetails.insert_one(
                scheduleToSave).inserted_id

            return ScheduleDetailsSchema(_id=str(inserted_id),
                                         line=str(arguments["line"]),
                                         startTime=lineData["startTime"],
                                         endTime=lineData["endTime"],
                                         classId=str(arguments["classId"]))

        return None

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

                # cehck if right now is break
                for i in range(0, len(schedule) - 1):
                    s1EndTime = schedule[i]["endTime"]
                    s2StartTime = schedule[i + 1]["startTime"]

                    endHour, endMinute, endSecond = map(
                        int, s1EndTime.split(":"))

                    startHour, startMinute, startSecond = map(
                        int, s2StartTime.split(":"))

                    startTime = datetime(currentTime.year, currentTime.month,
                                         currentTime.day, startHour, startMinute, startSecond)
                    endTime = datetime(currentTime.year, currentTime.month,
                                       currentTime.day, endHour, endMinute, endSecond)
                    if currentTime <= startTime and currentTime >= endTime:
                        s = schedule[i + 1]
                        startHour, startMinute, startSecond = map(
                            int, s["startTime"].split(":"))
                        endHour, endMinute, endSecond = map(
                            int, s["endTime"].split(":"))

                        startTime = datetime(currentTime.year, currentTime.month,
                                             currentTime.day, startHour, startMinute, startSecond)

                        endTime = datetime(currentTime.year, currentTime.month,
                                           currentTime.day, endHour, endMinute, endSecond)
                        return LatestLineSchema(_id=str(s["_id"]), line=s["line"], startTime=str(startTime), endTime=str(endTime))

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

    def resolve_rollMarkingActivites(self, info, arguments):
        arguments["activityType"] = 1
        activities = list(db.activities.find(arguments))
        activities.reverse()
        return map(lambda activity: RollMarkingActivitiesSchema(**activity), activities)


schema = graphene.Schema(query=Query, mutation=Mutation)
