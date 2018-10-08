import graphene

class ChatroomInput(graphene.InputObjectType):
    _id = graphene.ID()
    firstId = graphene.ID()
    secondId = graphene.ID()
    name = graphene.String()
