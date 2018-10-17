from flask import Blueprint

bp = Blueprint("email", __name__)

from app.controllers.email import routes
