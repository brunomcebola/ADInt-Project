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
    if request.method == "OPTIONS":
        return

    
    if "Authorization" not in request.headers:
        return jsonify("Authorization token required"), 407

    if request.headers["Authorization"] != "admin" and request.headers["Authorization"] != "user":
        return jsonify("Unauthorized"), 401


def check_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if "Authorization" not in request.headers:
            return jsonify("Authorization token required"), 407

        if request.headers["Authorization"] != "admin":
            return jsonify("Unauthorized"), 401

        return func(*args, **kwargs)

    return decorated_function


def check_user(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if "Authorization" not in request.headers:
            return jsonify("Authorization token required"), 407

        if request.headers["Authorization"] != "user":
            return jsonify("Unauthorized"), 401

        return func(*args, **kwargs)

    return decorated_function
