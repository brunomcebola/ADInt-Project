import yaml

from flask import  request


def check_auth_token():
    if "Token" not in request.headers:
        return "Proxy Authentication Required", 407

    if request.headers["Token"] != "proxy":
        return "Unauthorized", 401


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
