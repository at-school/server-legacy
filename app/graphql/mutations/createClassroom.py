import graphene
from flask_jwt_extended import get_jwt_identity

from app.database import db
from app.graphql.inputs.classroom import ClassroomInput
from app.graphql.schemas.classroom import ClassroomSchema


class CreateClassroom(graphene.Mutation):
    class Arguments:
        arguments = ClassroomInput(required=True)

    Output = ClassroomSchema

    def mutate(self, info, arguments):
        arguments["teacherUsername"] = get_jwt_identity()
        arguments["students"] = []
        if not arguments["teacherUsername"]:
            arguments["teacherUsername"] = "anhanhvina"
        db.classrooms.insert_one(arguments)
        return ClassroomSchema(**arguments)
