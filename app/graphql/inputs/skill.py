import graphene

class SkillInput(graphene.InputObjectType):
    _id = graphene.ID()
    name = graphene.String()
    color = graphene.String()
    userId = graphene.String()