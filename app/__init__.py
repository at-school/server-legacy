import ast
import base64
import os

import gevent
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_graphql import GraphQLView
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from flask_socketio import SocketIO

from app import models
from app.database import db
from app.graphql import schema
from config import Config

cors = CORS()
jwt = JWTManager()
socketio = SocketIO()


def graphql_view():
    view = GraphQLView.as_view(
        'graphql', schema=schema, graphiql=True, context={"user": ""})
    return jwt_required(view)


def create_app(config_class=Config):
    app = Flask(__name__, template_folder=config_class.TEMPLATE_URL,
                static_folder=config_class.STATIC_URL)
    app.config.from_object(config_class)

    cors.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app, async_mode="threading")

    from app.controllers.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.controllers.users import bp as users_bp
    app.register_blueprint(users_bp)

    from app.controllers.camera import bp as camera_bp
    app.register_blueprint(camera_bp)

    from app.controllers.messaging import bp as messaging_bp
    app.register_blueprint(messaging_bp)

    from app.controllers.email import bp as email_bp
    app.register_blueprint(email_bp)

    # from app.controllers.emojifier import bp as emojifier_bp
    # app.register_blueprint(emojifier_bp)

    # from app.controllers.schedule import bp as schedule_bp
    # app.register_blueprint(schedule_bp)

    from app.controllers.classroom import bp as classroom_bp
    app.register_blueprint(classroom_bp)

    # from app.controllers.errors import bp as errors_bp
    # app.register_blueprint(errors_bp)

    app.add_url_rule(
        '/graphql', view_func=graphql_view())

    @app.route("/", methods=["POST", "GET"])
    def mainView():
        if request.method == "POST":
            data = request.get_json()
            decoded_data = ast.literal_eval(base64.urlsafe_b64decode(
                data["message"]["data"]).decode("ascii"))
            emailAddress = decoded_data["emailAddress"]
            usersIds = [str(user.get("_id", "")) for user in list(db.users.find(
                {"loginedEmail": emailAddress}, {"_id": 1}))]

            for userId in usersIds:
                socketio.emit("email", room=userId)

            return jsonify({})
        return "sdfsdf"

    return app
