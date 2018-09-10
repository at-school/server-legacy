from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.controllers.errors import bad_request
from app.controllers.classroom import bp
from app.database import db
from app.decorators import teacher_required


@jwt_required
@teacher_required
@bp.route("/classroom/add/students", methods=["POST"])
def addStudents():
    try:
        data = request.get_json()
        studentList = data["studentList"]
        print(studentList)
        return jsonify({"data": True})
    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")
