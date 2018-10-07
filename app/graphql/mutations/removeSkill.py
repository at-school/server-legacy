import graphene
from bson.objectid import ObjectId
from graphql import GraphQLError

from app.database import db
from app.graphql.schemas.skill import SkillSchema
from app.graphql.inputs.skill import SkillInput


class RemoveSkill(graphene.Mutation):
    class Arguments:
        arguments = SkillInput(required=True)

    Output = SkillSchema

    def mutate(self, info, arguments):
        # get the id and removing by the id of the skill
        if not arguments["_id"]:
            raise GraphQLError("Not the right query")
        db.skills.delete_one({"_id": ObjectId(arguments["_id"])})

        return SkillSchema(_id=arguments["_id"])
