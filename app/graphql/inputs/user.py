import graphene

class UserInput(graphene.InputObjectType):
    _id = graphene.ID()
    username = graphene.String()
    firstname = graphene.String()
    lastname = graphene.String()
    password = graphene.String()
    accessLevel = graphene.Int()
    email = graphene.String()