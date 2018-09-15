from flask import request, jsonify, current_app, redirect, url_for
import os
from app.controllers.camera import bp
import base64
import face_recognition
from PIL import Image
import numpy as np
from app.controllers.errors import bad_request
import jwt
from app.models import User
from flask_jwt_extended import jwt_required
from app.database import db
from bson.objectid import ObjectId
from flask_jwt_extended import get_jwt_identity
import os


@bp.route("/camera/upload", methods=["POST"])
@jwt_required
def upload():
    try:
        data = request.get_json()
        image_data = data["imageData"]
        image_data = image_data[image_data.find(",")+1:]
        image_data = base64.b64decode(image_data)
        filename = 'image.jpg'
        with open(filename, 'wb') as f:
            f.write(image_data)
        # Load the uploaded image file
        img = face_recognition.load_image_file(os.path.join(
            os.path.dirname(os.path.realpath(__file__)), filename))
        # Get face encodings for any faces in the uploaded image
        unknown_face_encodings = face_recognition.face_encodings(img)
        people_found = []
        users = list(db.users.find(
            {}, {"faceEncoding": 1, "firstname": 1, "lastname": 1}))
        if len(unknown_face_encodings) > 0:

            # get only those users have face encoding
            known_face_encodings = []
            users_have_encodings = []
            for u in users:
                if u.get("faceEncoding", None):
                    known_face_encodings.append(
                        np.fromstring(u["faceEncoding"]))
                    users_have_encodings.append(u)

            # compare faces
            match_results = face_recognition.compare_faces(
                known_face_encodings, unknown_face_encodings[0])
            print(match_results)

            # get the name of all users that have the same face encodings
            for i in enumerate(match_results):
                if (i[1]):
                    user = users_have_encodings[i[0]]
                    people_found.append(
                        {"Id": str(user["_id"])})

        return jsonify({"success": True, "peopleFound": people_found})
    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")


@bp.route("/camera/save", methods=["POST"])
@jwt_required
def save_image():
    try:
        data = request.get_json()

        # get image data
        image_data = data["imageData"]
        image_data = base64.b64decode(image_data)
        filename = os.path.join(os.path.dirname(__file__), 'image.jpg')
        with open(filename, 'wb') as f:
            f.write(image_data)
        img = face_recognition.load_image_file(filename)
        face_encodings = face_recognition.face_encodings(img)
        if len(face_encodings) != 1:
            return bad_request("There is no face in the photo.")

        # put face encoding of the user into the database here
        encoding_to_save = face_encodings[0].tostring()
        db.users.update_one({'username': get_jwt_identity()}, {
                            "$set": {"faceEncoding": encoding_to_save}}, upsert=False)

        return jsonify({"success": True})
    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")
