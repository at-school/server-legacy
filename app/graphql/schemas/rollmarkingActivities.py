import graphene

class RollMarkingActivitiesSchema(graphene.ObjectType):
    _id = graphene.ID()
    activityType = graphene.Int()
    students = graphene.List(graphene.String)
    userId = graphene.ID()
    timestamp = graphene.DateTime()

from app.graphql.schemas.user import UserSchema