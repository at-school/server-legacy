import graphene
from bson.objectid import ObjectId
from graphql import GraphQLError

from app.database import db
from app.graphql.schemas.classroom import ClassroomSchema


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
