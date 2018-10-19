import base64
import os
import time
from calendar import day_name
from datetime import datetime, timedelta

import face_recognition
import gevent
import jwt
import numpy as np
import pymongo
from bson.objectid import ObjectId
from dateutil.parser import parse
from flask import current_app, jsonify, redirect, request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from PIL import Image

from app.controllers.camera import bp
from app.controllers.errors import bad_request
from app.database import db
from app.models import User


def getTimeDifference(time1, time2):
    """
        Return minutes difference between two time
        time1, time2: datetime object
    """
    d1_ts = time.mktime(time1.timetuple())
    d2_ts = time.mktime(time2.timetuple())

    return int(int(d2_ts-d1_ts) / 60)


@bp.route("/camera/upload", methods=["POST"])
@jwt_required
def upload():
    try:
        data = request.get_json()

        # the student list that hasn't been marked
        studentList = data["studentList"]
        if not studentList:
            return jsonify({"studentList": []})

        scheduleId = data["scheduleId"]
        userId = data["userId"]

        # get image data
        image_data = data["imageData"]
        image_data = image_data.split(",")[1]
        image_data = base64.b64decode(image_data)
        filename = os.path.join(os.path.dirname(__file__), 'image.jpeg')
        with open(filename, 'wb') as f:
            f.write(image_data)
        # Load the uploaded image file
        img = face_recognition.load_image_file(os.path.join(
            os.path.dirname(os.path.realpath(__file__)), filename))
        # Get face encodings for any faces in the uploaded image
        unknown_face_encodings = face_recognition.face_encodings(img)
        people_found = []

        if len(unknown_face_encodings) > 0:

            # get only those users have face encoding
            users_have_encodings = []
            for student in studentList:
                try:
                    student_encoding = np.loadtxt(os.path.join(os.path.dirname(
                        __file__), "encodings", student + ".txt"))
                    users_have_encodings.append(
                        {"student": student, "encoding": student_encoding})
                except OSError:
                    pass
            # compare faces
            match_results = face_recognition.compare_faces(
                [student["encoding"] for student in users_have_encodings], unknown_face_encodings[0])

            # get the name of all users that have the same face encodings
            for index, result in enumerate(match_results):
                if (result):
                    user = users_have_encodings[index]
                    people_found.append(user["student"])
        if (people_found):
            studentUpdated = []
            minsDiff = getTimeDifference(parse(data["startTime"]), parse(
                data["current"]).replace(tzinfo=None))
            for i in people_found:

                result = db.scheduleDetails.update({"_id": ObjectId(
                    scheduleId), "students._id": i, "students.inClass": False}, {"$set": {"students.$.inClass": True, "students.$.minsLate": minsDiff}})
                if (result["nModified"] > 0):
                    studentUpdated.append(i)
            now = datetime.now()
            if (studentUpdated):
                activity = {
                    "activityType": 1,
                    "userId": userId,
                    "students": studentUpdated,
                    "timestamp": now
                }
                insertedId = db.activities.insert_one(activity).inserted_id
                activity["Id"] = str(insertedId)
                del activity["_id"]
                activity["timestamp"] = str(now).split(".")[0]
                return jsonify(
                    {
                        "studentList": [dict(Id=studentId, minsLate=minsDiff) for studentId in studentUpdated],
                        "activity": activity
                    }
                )

        return jsonify({"studentList": []})
    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")


@bp.route("/camera/save", methods=["POST"])
@jwt_required
def save_image():
    try:
        data = request.get_json()
        filename = os.path.join(os.path.dirname(
            __file__), 'image.jpeg')
        with open(filename, 'wb') as f:
            # get image data
            image_data = data["imageData"]
            image_data = base64.b64decode(image_data)
            f.write(image_data)

        userId = get_jwt_identity()

        img = face_recognition.load_image_file(filename)
        face_encodings = face_recognition.face_encodings(img)
        if len(face_encodings) != 1:
            os.remove(filename)
            return bad_request("There is no face in the photo.")

        np.savetxt(os.path.join(os.path.dirname(
            __file__), "encodings", userId + ".txt"), face_encodings)
        os.remove(filename)

        return jsonify({"success": True})
    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")
