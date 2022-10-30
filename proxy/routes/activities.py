import os
import requests
from flask import Blueprint, request, jsonify

from proxy.middleware import *

activities = Blueprint("activities", __name__)

header = {"Token": str(os.getenv("TOKEN"))}

courses_url = os.getenv("COURSES_URL")
activities_url = os.getenv("ACTIVITIES_URL")
evaluations_url = os.getenv("EVALUATIONS_URL")
presential_services_url = os.getenv("PRESENTIAL_SERVICES_URL")

# Activities types


@activities.route("/activities/types")
def get_activities_types():
    req = requests.get("%s/activities/types" % activities_url, headers=header)
    return req.json(), req.status_code


@activities.route("/activity/type/<type_id>/<sub_type_id>")
def get_activity_type(type_id, sub_type_id):
    req = requests.get("%s/activity/type/%s/%s" % (activities_url, type_id, sub_type_id), headers=header)
    return req.json(), req.status_code


@activities.route("/activity/type/<type_id>/<sub_type_id>", methods=["DELETE"])
def delete_activity_type(type_id, sub_type_id):
    req = requests.delete("%s/activity/type/%s/%s" % (activities_url, type_id, sub_type_id), headers=header)
    return req.json(), req.status_code


@activities.route("/activity/type/create", methods=["POST"])
def create_activity_type():
    # TODO: check if db exists
    req = requests.post("%s/activity/type/create" % activities_url, json=request.json, headers=header)
    return req.json(), req.status_code


# Activities


@activities.route("/activities")
def get_activities():
    req = requests.get("%s/activities" % activities_url, headers=header)
    return req.json(), req.status_code


@activities.route("/activities/filter")
def get_filtered_activities():
    req = requests.get("%s/activities/filter" % activities_url, params=request.args.to_dict(), headers=header)
    return req.json(), req.status_code


@activities.route("/activity/<activity_id>", methods=["GET"])
def get_activity(activity_id):
    req = requests.get("%s/activity/%s" % (activities_url, activity_id), headers=header)
    return req.json(), req.status_code


@activities.route("/activity/<activity_id>", methods=["DELETE"])
def delete_activity(activity_id):
    req = requests.delete("%s/activity/%s" % (activities_url, activity_id), headers=header)
    return req.json(), req.status_code


@activities.route("/activity/create", methods=["POST"])
@check_json
def create_activity():
    mandatory_fileds = ["type_id", "sub_type_id"]

    for field in mandatory_fileds:
        if field not in request.json:  # type:ignore
            return jsonify("Field missing (%s)" % field), 400

    req = requests.get("%s/activity/type/%s/%s" % (activities_url, request.json["type_id"], request.json["sub_type_id"]), headers=header)  # type: ignore

    if req.status_code != 200:
        return req.json(), req.status_code

    activity_type = req.json()

    if activity_type["is_external"]:

        if "external_id" not in request.json:  # type: ignore
            return jsonify("Field missing (external_id)"), 400

        # CoursesDB
        if activity_type["external_db"] == "CoursesDB":
            req = requests.get("%s/course/%s" % (courses_url, request.json["external_id"]), headers=header)  # type: ignore
        # PresentialServicesDB
        else:
            req = requests.get("%s/service/%s" % (presential_services_url, request.json["external_id"]), headers=header)  # type: ignore

        if req.status_code != 200:
            return jsonify("No id %s in %s" % (request.json["external_id"], activity_type["external_db"])), req.status_code  # type: ignore

    req = requests.post("%s/activity/create" % activities_url, json=request.json, headers=header)

    return req.json(), req.status_code


@activities.route("/activity/start", methods=["POST"])
@check_json
def start_activity():

    mandatory_fileds = ["type_id", "sub_type_id"]

    for field in mandatory_fileds:
        if field not in request.json:  # type:ignore
            return jsonify("Bad Request"), 400

    req = requests.get("%s/activity/type/%s/%s" % (activities_url, request.json["type_id"], request.json["sub_type_id"]), headers=header)  # type: ignore

    if req.status_code != 200:
        return req.json(), req.status_code

    activity_type = req.json()

    if activity_type["is_external"]:

        if "external_id" not in request.json:  # type: ignore
            return jsonify("Field missing (external_id)"), 400

        # CoursesDB
        if activity_type["external_db"] == "CoursesDB":
            req = requests.get("%s/course/%s" % (courses_url, request.json["external_id"]), headers=header)  # type: ignore
        # PresentialServicesDB
        else:
            req = requests.get("%s/service/%s" % (presential_services_url, request.json["external_id"]), headers=header)  # type: ignore

        if req.status_code != 200:
            return jsonify("No id %s in %s" % (request.json["external_id"], activity_type["external_db"])), req.status_code  # type: ignore

    req = requests.post("%s/activity/start" % activities_url, json=request.json, headers=header)

    return req.json(), req.status_code


@activities.route("/activity/<activity_id>/stop", methods=["PUT"])
def stop_activity(activity_id):
    req = requests.put("%s/activity/%s/stop" % (activities_url, activity_id), headers=header)
    return req.json(), req.status_code
