import graphene


class ScheduleInput(graphene.InputObjectType):
    _id = graphene.ID()
    line = graphene.String()
    day = graphene.String()
    startTime = graphene.String()
    endTime = graphene.String()
