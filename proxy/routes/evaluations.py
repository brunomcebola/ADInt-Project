import os
import requests
from flask import Blueprint, request, jsonify

from middleware import *

evaluations = Blueprint("evaluations", __name__)

header = {"Token": str(os.getenv("TOKEN"))}

courses_url = os.getenv("COURSES_URL")
activities_url = os.getenv("ACTIVITIES_URL")
evaluations_url = os.getenv("EVALUATIONS_URL")
presential_services_url = os.getenv("PRESENTIAL_SERVICES_URL")

# Services


@evaluations.route("/services")
def get_services():
    req = requests.get("%s/services" % presential_services_url, headers=header)
    return req.json(), req.status_code


@evaluations.route("/services/filter")
def get_filtered_services():
    req = requests.get("%s/services/filter" % presential_services_url, params=request.args.to_dict(), headers=header)

    return req.json(), req.status_code


@evaluations.route("/service/<service_id>", methods=["GET"])
def get_service(service_id):
    req = requests.get("%s/service/%s" % (presential_services_url, service_id), headers=header)
    return req.json(), req.status_code


@evaluations.route("/service/<service_id>", methods=["DELETE"])
def delete_service(service_id):
    req = requests.delete("%s/service/%s" % (presential_services_url, service_id), headers=header)
    return req.json(), req.status_code


@evaluations.route("/service/<service_id>/evaluations")
def get_service_evaluations(service_id):
    req = requests.get("%s/evaluations/filter?service_id=%s" % (evaluations_url, service_id), headers=header)

    return req.json(), req.status_code


@evaluations.route("/service/create", methods=["POST"])
def create_service():
    if request.is_json and request.data:
        req = requests.post("%s/service/create" % presential_services_url, json=request.json, headers=header)
        return req.json(), req.status_code

    return jsonify("JSON with fields is mandatory"), 400
