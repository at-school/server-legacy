
import graphene
from bson.objectid import ObjectId

from app.database import db
from app.graphql.schemas.skill import SkillSchema
from app.graphql.inputs.skill import SkillInput


class CreateSkill(graphene.Mutation):
    class Arguments:
        arguments = SkillInput(required=True)

    Output = SkillSchema

    def mutate(self, info, arguments):

        inserted_id = db.skills.insert_one(
            {
                "name": arguments["name"],
                "color": arguments["color"],
                "userId": arguments["userId"]
            }
        ).inserted_id

        return SkillSchema(
            _id=str(inserted_id), name=arguments["name"], color=arguments["color"], userId=arguments["userId"])
