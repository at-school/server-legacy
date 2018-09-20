import graphene


class ScheduleDetailsInput(graphene.InputObjectType):
    classId = graphene.String()
    line = graphene.String()
    teacherUsername = graphene.String()
