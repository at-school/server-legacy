import graphene

class StudentsScheduleDetails(graphene.ObjecType):
    _id = graphene.ID()
    inClass = graphene.Boolean()
    minsLate = graphene.Int()

class ScheduleDetailsSchema(graphene.ObjecType):
    _id = graphene.ID()
    line = graphene.String()
    createdTime = graphene.DateTime()
    date = graphene.DateTime()
