from datetime import datetime
from hashlib import md5

import graphene

from app.database import db
from app.graphql.inputs.user import UserInput
from app.graphql.schemas.user import UserSchema
from app.models import User


class CreateUser(graphene.Mutation):
    class Arguments:
        arguments = UserInput(required=True)

    Output = UserSchema

    def mutate(self, info, arguments):
        u = User(**arguments)
        u.setPassword(arguments.password)
        inserted_id = str(db.users.insert_one({
            "username": u.username,
            "password": u.password,
            "firstname": u.firstname,
            "lastname": u.lastname,
            "email": u.email,
            "accessLevel": u.accessLevel,
            "avatar": u.avatar,
            "studentClassroom": [],
            "faceEncoding": "",
            "activities": []
        }).inserted_id)
        timestamp = datetime.utcnow()
        inserted_id = str(db.chatrooms.insert_one({
            "users": [inserted_id],
            "timestamp": timestamp,
            "name": "Team @ School"
        }).inserted_id)
        avatar_digest = md5(
            "phamduyanh249@live.com".lower().encode('utf-8')).hexdigest()
        db.messages.insert_one(
            {
                "messageContent": "Hello, welcome to @ School!",
                "chatroomId": inserted_id,
                "senderId": "",
                "timestamp": timestamp,
                "senderAvatar": 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
                    avatar_digest, 512)
            }
        )

        return UserSchema(**arguments, avatar=u.avatar)
