from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.controllers.errors import bad_request
from app.controllers.users import bp
from app.database import db


@jwt_required
@bp.route("/user/search", methods=["POST"])
def signin():
    try:
        data = request.get_json()
        searchPattern = data["searchPattern"]
        users = list(db.users.find({"username": {"$regex": searchPattern}}))
        users = list(map(lambda user: {"_id": str(
            user["_id"]), "firstname": user["firstname"], "lastname": user["lastname"], "avatar": user["avatar"]}, users))
        print(users)
        return jsonify({"data": users})
    except KeyError:
        return bad_request("Wrong arguments.")
    return bad_request("There is an internal server error. Please contact the IT support.")
