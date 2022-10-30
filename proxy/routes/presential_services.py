import os
import requests
from flask import Blueprint, request, jsonify

from middleware import *

presential_services = Blueprint("presential_services", __name__)

header = {"Token": str(os.getenv("TOKEN"))}

courses_url = os.getenv("COURSES_URL")
activities_url = os.getenv("ACTIVITIES_URL")
evaluations_url = os.getenv("EVALUATIONS_URL")
presential_services_url = os.getenv("PRESENTIAL_SERVICES_URL")

# Evaluations


@presential_services.route("/evaluations")
def get_evaluations():
    req = requests.get("%s/evaluations" % evaluations_url, headers=header)
    return req.json(), req.status_code


@presential_services.route("/evaluations/filter")
def get_filtered_evaluations():

    req = requests.get("%s/evaluations/filter" % evaluations_url, params=request.args.to_dict(), headers=header)

    return req.json(), req.status_code


@presential_services.route("/evaluation/<evaluation_id>", methods=["GET"])
def get_evaluation(evaluation_id):
    req = requests.get("%s/evaluation/%s" % (evaluations_url, evaluation_id), headers=header)
    return req.json(), req.status_code


@presential_services.route("/evaluation/<evaluation_id>", methods=["DELETE"])
def delete_evaluation(evaluation_id):
    req = requests.delete("%s/evaluation/%s" % (evaluations_url, evaluation_id), headers=header)
    return req.json(), req.status_code


@presential_services.route("/evaluation/create", methods=["POST"])
def create_evaluation():
    if request.is_json and request.data:
        mandatory_fileds = ["service_id"]

        for field in mandatory_fileds:
            if field not in request.json:  # type:ignore
                return jsonify("Bad Request"), 400

        req = requests.get("%s/service/%s" % (services_url, request.json["service_id"]), headers=header)  # type: ignore

        if req.status_code != 200:
            return req.json(), req.status_code

        req = requests.post("%s/evaluation/create" % evaluations_url, json=request.json, headers=header)

        return req.json(), req.status_code

    return jsonify("JSON with fields is mandatory"), 400
