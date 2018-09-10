import graphene
from bson.objectid import ObjectId

from app.database import db
from app.graphql.schemas.user import UserSchema


class AddStudentToClassroomInput(graphene.InputObjectType):
    classId = graphene.ID()
    studentId = graphene.ID()


class AddStudentToClassroom(graphene.Mutation):
    class Arguments:
        arguments = AddStudentToClassroomInput(required=True)

    Output = UserSchema

    def mutate(self, info, arguments):
        print("Here")
        db.classrooms.update({'_id': ObjectId(arguments["classId"])}, {
                             '$push': {'students': arguments["studentId"]}})
        db.users.update({'_id': ObjectId(arguments["studentId"])}, {
                             '$push': {'studentClassroom': arguments["classId"]}})
        user = db.users.find_one({"_id": ObjectId(arguments["studentId"])})
        return UserSchema(**user)
