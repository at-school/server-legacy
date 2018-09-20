import graphene

class LatestLineSchema(graphene.ObjectType):
    _id = graphene.ID()
    line = graphene.String()
    startTime = graphene.String()
    endTime = graphene.String()

    