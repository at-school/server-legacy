import graphene
from bson.objectid import ObjectId
from app.database import db


class EmailSchema(graphene.ObjectType):
    _id = graphene.ID()
    dateTime = graphene.String()
    From = graphene.String()
    FromEmail = graphene.String()
    subject = graphene.String()
    html = graphene.String()
    userId = graphene.String()