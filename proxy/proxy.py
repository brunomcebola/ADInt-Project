import requests
from flask import Flask, request, jsonify


from aux_functions import *


header = {"Token": "proxy"}

# read and validate configurations
config_file = "./config.yaml"

configs = read_yaml(config_file)

validate_yaml(
    configs, ["host", "port", "ps_host", "ps_port", "e_host", "e_port", "c_host", "c_port", "a_host", "a_port"], config_file
)

services_url = "http://%s:%s" % (configs["ps_host"], configs["ps_port"])
evaluations_url = "http://%s:%s" % (configs["e_host"], configs["e_port"])
courses_url = "http://%s:%s" % (configs["c_host"], configs["c_port"])
activities_url = "http://%s:%s" % (configs["a_host"], configs["a_port"])

app = Flask(__name__)


@app.errorhandler(requests.exceptions.ConnectionError)
def handle_bad_request(e):
    return jsonify("Bad Gateway"), 502


# Services


@app.route("/services")
def get_services():
    req = requests.get("%s/services" % services_url, headers=header)
    return req.json(), req.status_code


@app.route("/services/filter")
def get_filtered_services():
    req = requests.get("%s/services/filter" % services_url, params=request.args.to_dict(), headers=header)

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
    req = requests.get("%s/evaluations/filter?service_id=%s" % (evaluations_url, service_id), headers=header)

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
    return req.json(), req.status_code


@app.route("/evaluations/filter")
def get_filtered_evaluations():

    req = requests.get("%s/evaluations/filter" % evaluations_url, params=request.args.to_dict(), headers=header)

    return req.json(), req.status_code


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

    return jsonify("Bad Request"), 400


# Courses


@app.route("/courses")
def get_courses():
    req = requests.get("%s/courses" % courses_url, headers=header)
    return req.json(), req.status_code


@app.route("/courses/filter")
def get_filtered_courses():
    req = requests.get("%s/courses/filter" % courses_url, params=request.args.to_dict(), headers=header)

    return req.json(), req.status_code


@app.route("/course/<course_id>", methods=["GET"])
def get_course(course_id):
    req = requests.get("%s/course/%s" % (courses_url, course_id), headers=header)
    return req.json(), req.status_code


@app.route("/course/<course_id>", methods=["DELETE"])
def delete_course(course_id):
    req = requests.delete("%s/course/%s" % (courses_url, course_id), headers=header)
    return req.json(), req.status_code


@app.route("/course/create", methods=["POST"])
def create_course():
    if request.is_json and request.data:
        req = requests.post("%s/course/create" % courses_url, json=request.json, headers=header)
        return req.json(), req.status_code

    return jsonify("Bad Request"), 400


# Activities


@app.route("/activities")
def get_activities():
    req = requests.get("%s/activities" % activities_url, headers=header)
    return req.json(), req.status_code


@app.route("/activities/filter")
def get_filtered_activities():
    req = requests.get("%s/activities/filter" % activities_url, params=request.args.to_dict(), headers=header)

    return req.json(), req.status_code


@app.route("/activities/types")
def get_activities_types():
    req = requests.get("%s/activities/types" % activities_url, headers=header)
    return req.json(), req.status_code


@app.route("/activity/type/<type_id>/<sub_type_id>/db")
def get_activity_db(type_id, sub_type_id):
    req = requests.get("%s/activity/type/%s/%s/db" % (activities_url, type_id, sub_type_id), headers=header)        
    return jsonify(req.json()), req.status_code


@app.route("/activity/<activity_id>", methods=["GET"])
def get_activity(activity_id):
    req = requests.get("%s/activity/%s" % (activities_url, activity_id), headers=header)
    return req.json(), req.status_code


@app.route("/activity/<activity_id>", methods=["DELETE"])
def delete_activity(activity_id):
    req = requests.delete("%s/activity/%s" % (activities_url, activity_id), headers=header)
    return req.json(), req.status_code


@app.route("/activity/create", methods=["POST"])
def create_activity():
    if request.is_json and request.data:

        mandatory_fileds = ["type_id", "sub_type_id"]

        for field in mandatory_fileds:
            if field not in request.json:  # type:ignore
                return jsonify("Bad Request"), 400

        req = requests.get("%s/activity/type/%s/%s/db" % (activities_url, request.json["type_id"], request.json["sub_type_id"]), headers=header)  # type: ignore

        if req.status_code != 200:
            return req.json(), req.status_code

        if req.json():
            if "external_id" not in request.json:  # type: ignore
                return jsonify("Bad Request"), 400

            else:
                if req.json() == "CoursesDB":
                    req = requests.get("%s/course/%s" % (courses_url, request.json["external_id"]), headers=header)  # type: ignore
                elif req.json() == "PresentialServicesDB":
                    req = requests.get("%s/service/%s" % (services_url, request.json["external_id"]), headers=header)  # type: ignore

                if req.status_code != 200:
                    return req.json(), req.status_code

        req = requests.post("%s/activity/create" % activities_url, json=request.json, headers=header)

        return req.json(), req.status_code

    return jsonify("Bad Request"), 400


@app.route("/activity/start", methods=["POST"])
def start_activity():
    if request.is_json and request.data:

        mandatory_fileds = ["type_id", "sub_type_id"]

        for field in mandatory_fileds:
            if field not in request.json:  # type:ignore
                return jsonify("Bad Request"), 400

        req = requests.get("%s/activity/type/%s/%s/db" % (activities_url, request.json["type_id"], request.json["sub_type_id"]), headers=header)  # type: ignore

        if req.status_code != 200:
            return req.json(), req.status_code

        if req.json():
            if "external_id" not in request.json:  # type: ignore
                return jsonify("Bad Request"), 400

            else:
                if req.json() == "CoursesDB":
                    req = requests.get("%s/course/%s" % (courses_url, request.json["external_id"]), headers=header)  # type: ignore
                elif req.json() == "PresentialServicesDB":
                    req = requests.get("%s/service/%s" % (services_url, request.json["external_id"]), headers=header)  # type: ignore

                if req.status_code != 200:
                    return req.json(), req.status_code

        req = requests.post("%s/activity/start" % activities_url, json=request.json, headers=header)

        return req.json(), req.status_code

    return jsonify("Bad Request"), 400


@app.route("/activity/<activity_id>/stop", methods=["PUT"])
def stop_activity(activity_id):
    req = requests.put("%s/activity/%s/stop" % (activities_url, activity_id), headers=header)
    return req.json(), req.status_code


################################
############ MAIN ##############


if __name__ == "__main__":
    app.run(host=configs["host"], port=configs["port"], debug=True)
