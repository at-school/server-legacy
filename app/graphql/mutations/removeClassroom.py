import os
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
        os.remove(os.path.join(os.getcwd(), "class_images", arguments["_id"] + ".txt"))
        db.users.update_many({"accessLevel": 1}, {'$pull': {'studentClassroom': arguments["_id"]}})
        return ClassroomSchema(**arguments)
