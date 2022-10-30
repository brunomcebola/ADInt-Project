import yaml

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

def read_yaml(file_path: str):
    try:
        with open(file_path, "r") as stream:
            try:
                configs = yaml.safe_load(stream)

                if configs == None:
                    raise SystemExit("O ficheiro de configurações (%s) está vazio." % file_path)

                return configs

            except:
                raise SystemExit("Erro ao ler ficheiro de configurações (%s)." % file_path)
    except:
        raise SystemExit("Ficheiro de configurações (%s) não encontrado." % file_path)


def validate_yaml(config: dict, keys_to_verify: list, file_path: str):
    for key in keys_to_verify:
        if key not in config:
            raise SystemExit("Parâmetro '%s' em falta no ficheiro de configurações (%s)." % (key, file_path))
