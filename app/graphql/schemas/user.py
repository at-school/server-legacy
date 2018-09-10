import graphene

from app.database import db


class UserSchema(graphene.ObjectType):
    username = graphene.String()
    firstname = graphene.String()
    lastname = graphene.String()
    password = graphene.String()
    accessLevel = graphene.Int()
    email = graphene.String()
    avatar = graphene.String()
    classrooms = graphene.List(lambda: ClassroomSchema)
    chatrooms = graphene.List(lambda: ChatroomSchema)
    latestChatroom = graphene.List(lambda: ChatroomSchema)
    studentClassroom = graphene.List(lambda: ClassroomSchema)
    _id = graphene.ID()

    def resolve_classrooms(self, info):
        classrooms = list(db.classrooms.find(
            {"teacherUsername": self.username}))
        return map(lambda i: ClassroomSchema(**i), classrooms)


from app.graphql.schemas.chatroom import ChatroomSchema
from app.graphql.schemas.classroom import ClassroomSchema

