import graphene
from bson.objectid import ObjectId

from app.database import db
from app.graphql.inputs.classroom import ClassroomInput
from app.graphql.schemas.classroom import ClassroomSchema


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
