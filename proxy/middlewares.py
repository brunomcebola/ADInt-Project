from functools import wraps
from flask import request, jsonify


def check_json(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not (request.is_json and request.data):
            return jsonify("Its is mandatory to provide a JSON with data"), 400

        return func(*args, **kwargs)

    return decorated_function

def check_permission():
    if "ADMIN_TOKEN" not in request.headers and "USER_TOKEN" not in request.headers:
        return jsonify("Neither an Admin nor an User Authentication Required"), 407

def check_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if "ADMIN_TOKEN" not in request.headers:
            return jsonify("Admin Authentication Required"), 407

        if request.headers["ADMIN_TOKEN"] != "admin":
            return jsonify("Unauthorized"), 401
        
        return func(*args, **kwargs)

    return decorated_function


def check_user(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if "USER_TOKEN" not in request.headers:
            return jsonify("User Authentication Required"), 407

        if request.headers["USER_TOKEN"] != "user":
            return jsonify("Unauthorized"), 401
        
        return func(*args, **kwargs)
        
    return decorated_function