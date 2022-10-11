from flask import Flask, request, jsonify

import requests

from auxFunctions import *

header = {"Token": "proxy"}

# read and validate configurations
config_file = "./config.yaml"

configs = read_yaml(config_file)

validate_yaml(configs, ["host", "port", "ps_host", "ps_port", "e_host", "e_port"], config_file)

services_url = "http://%s:%s" % (configs["ps_host"], configs["ps_port"])
evaluations_url = "http://%s:%s" % (configs["e_host"], configs["e_port"])

app = Flask(__name__)

# Services


@app.route("/services")
def get_services():
    req = requests.get("%s/services" % services_url, headers=header)
    return req.json(), req.status_code


@app.route("/service/<service_id>", methods=["GET"])
def get_service(service_id):
    req = requests.get("%s/service/%s" % (services_url, service_id), headers=header)
    return req.json(), req.status_code


@app.route("/service/<service_id>", methods=["DELETE"])
def delete_service(service_id):
    req = requests.delete("%s/service/%s" % (services_url, service_id), headers=header)
    return req.json(), req.status_code


@app.route("/service/<service_id>/evaluations")
def get_service_evaluations(service_id):
    req = requests.get("%s/service/%s" % (services_url, service_id), headers=header)

    if req.status_code != 200:
        return req.json(), req.status_code

    req = requests.get("%s/evaluations/service/%s" % (evaluations_url, service_id), headers=header)

    return req.json(), req.status_code


@app.route("/service/create", methods=["POST"])
def create_service():
    if request.is_json and request.data:
        req = requests.post("%s/service/create" % services_url, json=request.json, headers=header)
        return req.json(), req.status_code

    return jsonify("Bad Request"), 400


# Evaluations


@app.route("/evaluations")
def get_evaluations():
    req = requests.get("%s/evaluations" % evaluations_url, headers=header)
    return req.json()


@app.route("/evaluation/<evaluation_id>", methods=["GET"])
def get_evaluation(evaluation_id):
    req = requests.get("%s/evaluation/%s" % (evaluations_url, evaluation_id), headers=header)
    return req.json(), req.status_code


@app.route("/evaluation/<evaluation_id>", methods=["DELETE"])
def delete_evaluation(evaluation_id):
    req = requests.delete("%s/evaluation/%s" % (evaluations_url, evaluation_id), headers=header)
    return req.json(), req.status_code


@app.route("/evaluation/create", methods=["POST"])
def create_evaluation():
    if request.is_json and request.json:

        if "service_id" not in request.json:
            return jsonify("Bad Request"), 400

        req = requests.get("%s/service/%s" % (services_url, request.json["service_id"]), headers=header)

        if req.status_code != 200:
            return req.json(), req.status_code

        req = requests.post("%s/evaluation/create" % evaluations_url, json=request.json, headers=header)

        return req.json(), req.status_code

    return jsonify("Bad Request"), 400


# Courses


@app.route("/createCourse", methods=["GET", "POST"])
def createCourse():
    dicToSend = {"title": "doProxy", "description": "hello world", "location": "jerusalem"}
    req = requests.post("http://127.0.0.1:8001/createCourse", json=dicToSend, headers=header)
    return req.json()


@app.route("/listCourses")
def getAllCourses():
    req = requests.get("http://127.0.0.1:8001/listCourses", headers=header)
    return req.json()


# Activities


@app.route("/createActivity", methods=["GET", "POST"])
def createActivity():
    dicToSend = {"title": "doProxy", "description": "hello world", "location": "jerusalem"}
    req = requests.post("http://127.0.0.1:8002/createActivity", json=dicToSend, headers=header)
    return req.json()


@app.route("/listActivities")
def getAllActivities():
    req = requests.get("http://127.0.0.1:8002/listActivities")
    return req.json()


################################
############ MAIN ##############


if __name__ == "__main__":
    app.run(host=configs["host"], port=configs["port"], debug=True)
