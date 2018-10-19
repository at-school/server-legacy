import graphene
from bson.objectid import ObjectId

from app.database import db
from app.graphql.schemas.user import UserSchema


class RemoveStudentFromClassroomInput(graphene.InputObjectType):
    classId = graphene.ID()
    studentId = graphene.ID()


class RemoveStudentFromClassroom(graphene.Mutation):
    class Arguments:
        arguments = RemoveStudentFromClassroomInput(required=True)

    Output = UserSchema

    def mutate(self, info, arguments):
        db.classrooms.update({'_id': ObjectId(arguments["classId"])}, {
                             '$pull': {'students': arguments["studentId"]}})
        db.users.update({'_id': ObjectId(arguments["studentId"])}, {
                             '$pull': {'studentClassroom': arguments["classId"]}})
        user = db.users.find_one({"_id": ObjectId(arguments["studentId"])})
        return UserSchema(**user)
