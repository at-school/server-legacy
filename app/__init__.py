import os

from flask import Flask, request
from flask_cors import CORS
from flask_graphql import GraphQLView
from flask_jwt_extended import (
    JWTManager,
    jwt_required
)
from flask_socketio import SocketIO

from app import models
from app.graphql import schema
from config import Config

cors = CORS()
jwt = JWTManager()
socketio = SocketIO()


def graphql_view():
    view = GraphQLView.as_view(
        'graphql', schema=schema, graphiql=True, context={"user": ""})
    return view


def create_app(config_class=Config):
    app = Flask(__name__, template_folder=config_class.TEMPLATE_URL,
                static_folder=config_class.STATIC_URL)
    app.config.from_object(config_class)

    cors.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)

    from app.controllers.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.controllers.users import bp as users_bp
    app.register_blueprint(users_bp)

    from app.controllers.camera import bp as camera_bp
    app.register_blueprint(camera_bp)

    from app.controllers.messaging import bp as messaging_bp
    app.register_blueprint(messaging_bp)

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

    return app
