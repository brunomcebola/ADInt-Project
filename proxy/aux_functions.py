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
