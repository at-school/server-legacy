import graphene

class ClassroomInput(graphene.InputObjectType):
    _id = graphene.ID()
    name = graphene.String()
    description = graphene.String()
    avatar = graphene.String()
    teacherUsername = graphene.String()
    lineId = graphene.String()
    falcutyId = graphene.String()