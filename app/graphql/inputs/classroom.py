import graphene

class ClassroomInput(graphene.InputObjectType):
    _id = graphene.ID()
    name = graphene.String()
    description = graphene.String()
    avatar = graphene.String()
    teacherId = graphene.String()
    lineId = graphene.String()
    falcutyId = graphene.String()