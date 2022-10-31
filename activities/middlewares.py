from functools import wraps
from flask import request, jsonify


def check_json(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not (request.is_json and request.data):
            return jsonify("Its is mandatory to provide a JSON with data"), 400

        return func(*args, **kwargs)

    return decorated_function


def check_auth_token():
    if "Token" not in request.headers:
        return jsonify("Proxy Authentication Required"), 407

    if request.headers["Token"] != "proxy":
        return jsonify("Unauthorized"), 401
