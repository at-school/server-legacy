import graphene

from app.database import db
from app.graphql.inputs.user import UserInput
from app.models import User
from app.graphql.schemas.user import UserSchema

class CreateUser(graphene.Mutation):
    class Arguments:
        arguments = UserInput(required=True)

    Output = UserSchema

    def mutate(self, info, arguments):
        u = User(**arguments)
        u.setPassword(arguments.password)
        db.users.insert_one({
            "username": u.username,
            "password": u.password,
            "firstname": u.firstname,
            "lastname": u.lastname,
            "email": u.email,
            "accessLevel": u.accessLevel,
            "avatar": u.avatar,
            "studentClassroom": []
        })
        return UserSchema(**arguments, avatar=u.avatar)
