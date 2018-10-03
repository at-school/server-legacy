import graphene

class SkillSchema(graphene.ObjectType):
    _id = graphene.ID()
    name = graphene.String()
    color = graphene.String()
    userId = graphene.String()