import graphene
from flask_jwt_extended import get_jwt_identity

from app.database import db
from app.graphql.inputs.classroom import ClassroomInput
from app.graphql.schemas.classroom import ClassroomSchema

import os


class CreateClassroom(graphene.Mutation):
    class Arguments:
        arguments = ClassroomInput(required=True)

    Output = ClassroomSchema

    def mutate(self, info, arguments):
        arguments["teacherUsername"] = get_jwt_identity()
        arguments["students"] = []

        # get and delete avatar in order to save it in local server
        avatar = arguments["avatar"]
        del arguments["avatar"]
        
        if not arguments["teacherUsername"]:
            arguments["teacherUsername"] = "anhanhvina"
        inserted_id = db.classrooms.insert_one(arguments).inserted_id
        class_image_path = os.path.join(os.getcwd(), "class_images", str(inserted_id) + ".txt")

        with open(class_image_path, "w+") as f:
            f.write(avatar)
            arguments["avatar"] = avatar

        return ClassroomSchema(**arguments)
