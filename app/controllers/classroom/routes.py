from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.controllers.errors import bad_request
from app.controllers.classroom import bp
from app.database import db
from app.decorators import teacher_required
from bson.objectid import ObjectId


@jwt_required
@teacher_required
# add students to the latest schedule, if applicable
@bp.route("/classroom/schedule/students", methods=["POST"])
def addStudents():
    try:
        data = request.get_json()
        studentList = data["studentList"]
        scheduleId = data["scheduleId"]
        schedule = db.scheduleDetails.find_one({"_id": ObjectId(scheduleId)})
        scheduleStudents = list(map(lambda student: student["_id"],schedule["students"]))
        for student in scheduleStudents:
            if student in studentList:
                studentList.remove(student)

        db.scheduleDetails.update({"_id": ObjectId(scheduleId)}, {"$push": {"students": {"$each": list(map(lambda student: {"_id": student, "inClass": False},studentList))}}})
        
        print(studentList)
        return jsonify({"studentList": studentList})
    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")
