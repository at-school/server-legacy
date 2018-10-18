import graphene

class EmailInput(graphene.InputObjectType):
    _id = graphene.ID()
    userId = graphene.String()