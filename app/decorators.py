from functools import wraps

from flask import jsonify
from flask_jwt_extended import (JWTManager, create_access_token,
                                get_jwt_claims, verify_jwt_in_request)

from app.controllers.errors import bad_request

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if int(claims['role']) < 3:
            return bad_request("You don't have enough access")
        else:
            return fn(*args, **kwargs)
    return wrapper

def teacher_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if int(claims['role']) < 2:
            return bad_request("You don't have enough access")
        else:
            return fn(*args, **kwargs)
    return wrapper

def student_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if int(claims['role']) < 1:
            return bad_request("You don't have enough access")
        else:
            return fn(*args, **kwargs)
    return wrapper
