import jwt
from app import db
from app.controllers.classroom import bp
from app.models import Class, User, Task
from config import Config
from flask import current_app, jsonify, request, bad_request

"""
Create or edit a class for a user.
Arguments:
  - className: the name of the class
  - classDescription: the description of the class
  - classLine: the line of the class
  - classFalcuty: the falcuty id of the class
  - token: access token for the user
Returns: 
  - id: the id of the new class
"""
@bp.route("/classroom/createclass", methods=["POST"])
def create_class():
    try:
        data = request.get_json()
        id = data.get("id", None)
        class_name = data["className"]
        class_description = data["classDescription"]
        class_line = data["classLine"]
        class_falcuty = data["classFalcuty"]
        avatar_data = data["classImageData"]

        # get user from jwt token
        token = data["token"]
        payload = jwt.decode(token, open(current_app.config["JWT_KEY_PUBLIC"]).read(), algorithms=['RS256'])
        user = User.query.filter_by(id=payload["id"]).first()
        if not user:
            return bad_request("User does not exist.")

        if id:
            c = Class.query.filter_by(id=int(id)).first()

            if not c:
                return bad_request("Class does not exist.")
            
            c.name = class_name
            c.description = class_description
            c.class_line = class_line
            c.class_falcuty = class_falcuty
            c.avatar_data = avatar_data
            db.session.commit()

            return jsonify({"id": id})

            

        # check if user has enough access level
        if user.access_level != 2:
            return bad_request("Do not have access.")
        
        new_class = Class(name=class_name, description=class_description, 
                    line_id=int(class_line), falcuty_id=int(class_falcuty),
                    teacher_id=user.id, avatar_data=avatar_data)
        
        db.session.add(new_class)
        db.session.commit()
        
        return jsonify({"id": new_class.id})

    except KeyError:
        pass

"""
Get all class of an user. Need the access token of that user
Return a dictionary with class id, class name, class description, and class line.
"""
@bp.route("/classroom/teacher/getclass", methods=["POST"])
def get_class_teacher():
    try:
        data = request.get_json()

        # get user from jwt token
        token = data["token"]
        payload = jwt.decode(token, open(current_app.config["JWT_KEY_PUBLIC"]).read(), algorithms=['RS256'])
        user = User.query.filter_by(id=payload["id"]).first()

        if not user:
            return bad_request("User does not exist.")

        # check if user has enough access level
        if user.access_level != 2:
            return bad_request("Do not have access.")

        classes = Class.query.filter_by(teacher_id=user.id)
        results = []
        for c in classes:
            results.append({
                "id": str(c.id),
                "name": c.name,
                "description": c.description,
                "line": c.line_id,
                "falcuty": c.falcuty_id,
                "avatarData": c.avatar_data
            })
        return jsonify({"results": results})

    except KeyError:
        pass

@bp.route("/classroom/teacher/removeclass", methods=["POST"])
def remove_class():
    try:
        data = request.get_json()

        # get user from jwt token
        token = data["token"]
        payload = jwt.decode(token, open(current_app.config["JWT_KEY_PUBLIC"]).read(), algorithms=['RS256'])
        user = User.query.filter_by(id=payload["id"]).first()
        class_id = data["id"]

        if not user:
            return bad_request("User does not exist.")

        Class.query.filter_by(id=int(class_id)).delete()
        db.session.commit()

        return jsonify({})
    
    except KeyError:
        pass

"""
Check if whether an user has any class.
If yes, then return a dictionary which contains a true 'result' key and a list of all classes that user has,
otherwise, return a dictionary containg a false 'result' key
"""
@bp.route("/classroom/teacher/hasclass", methods=["POST"])
def teacher_has_class():
    try:
        data = request.get_json()

        # get user from jwt token
        token = data["token"]
        payload = jwt.decode(token, open(current_app.config["JWT_KEY_PUBLIC"]).read(), algorithms=['RS256'])
        user = User.query.filter_by(id=payload["id"]).first()

        if not user:
            return bad_request("User does not exist.")

        # check if user has enough access level
        if user.access_level != 2:
            return bad_request("Do not have access.")

        classes = Class.query.filter_by(teacher_id=user.id).all()
        for i in range(len(classes)):
            classes[i] = {
                "id": classes[i].id
            }
        if len(classes) == 0:
            return jsonify({"result": False})
        else:
            return jsonify({"result": True, "classes": classes})

    except KeyError:
        pass

@bp.route("/classroom/addtask", method=["POST"])
def addtask():
    try:
        data = request.get_json()

        # get user from jwt token
        token = data["token"]
        payload = jwt.decode(token, open(
            current_app.config["JWT_KEY_PUBLIC"]).read(), algorithms=['RS256'])
        user = User.query.filter_by(id=payload["uid"]).first()
        class_ = Class.query.filter_by(id=payload["cid"]).first()
        if not user:
            return bad_request("User does not exist.")

        # check if user has enough access level
        if user.access_level != 2:
            return bad_request("Do not have access.")

        task = Task(
            class_id=class_.id, title=payload['title'], desc=payload['desc'],
            users=payload['users'], due_date=payload['due'], active=True
        )

        return jsonify({"result": True, "task_id": task.id})

    except KeyError:
        pass
