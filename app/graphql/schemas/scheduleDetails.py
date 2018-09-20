import graphene
from app.database import db
from bson.objectid import ObjectId


class StudentsScheduleDetailsSchema(graphene.ObjectType):
    _id = graphene.ID()
    inClass = graphene.Boolean()
    studentDetails = graphene.Field(lambda: UserSchema)

    def resolve_studentDetails(self, info):
        user = db.users.find_one({"_id": ObjectId(self._id)})
        return UserSchema(**user)


class ScheduleDetailsSchema(graphene.ObjectType):
    _id = graphene.ID()
    line = graphene.String()
    startTime = graphene.String()
    endTime = graphene.String()
    classId = graphene.String()
    students = graphene.List(lambda: StudentsScheduleDetailsSchema)

    def resolve_students(self, info):
        schedule = db.scheduleDetails.find_one(
            {"_id": ObjectId(self._id)}, {"students": 1})
        students = schedule["students"]
        return map(lambda student: StudentsScheduleDetailsSchema(_id=student["_id"], inClass=student["inClass"]), students)


from app.graphql.schemas.user import UserSchema
