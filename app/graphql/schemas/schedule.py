import graphene


class ScheduleSchema(graphene.ObjectType):
    _id = graphene.ID()
    line = graphene.String()
    day = graphene.String()
    startTime = graphene.String()
    endTime = graphene.String()
