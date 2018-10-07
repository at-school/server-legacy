import graphene
from bson.objectid import ObjectId
from app.database import db
from app.graphql.schemas.user import UserSchema

class ClassroomSchema(graphene.ObjectType):
    _id = graphene.ID()
    name = graphene.String()
    description = graphene.String()
    avatar = graphene.String()
    teacherUsername = graphene.String()
    lineId = graphene.String()
    falcutyId = graphene.String()
    students = graphene.List(lambda: UserSchema)

    def resolve_students(self, info):
        classroomData = db.classrooms.find_one({"_id": ObjectId(self._id)})
        studentList = classroomData["students"]
        studentList = map(lambda student: db.users.find_one(
            {"_id": ObjectId(student)}),  studentList)
        return map(lambda student: UserSchema(**student), studentList)

