import graphene

class RollMarkingActivitiesInput(graphene.InputObjectType):
    userId = graphene.ID()
