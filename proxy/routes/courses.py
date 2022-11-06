import os
import requests
from flask import Blueprint, request, jsonify

from middlewares import *

courses = Blueprint("courses", __name__)

header = {"Token": str(os.getenv("TOKEN"))}

courses_url = os.getenv("COURSES_URL")
activities_url = os.getenv("ACTIVITIES_URL")
evaluations_url = os.getenv("EVALUATIONS_URL")
presential_services_url = os.getenv("PRESENTIAL_SERVICES_URL")

# Courses


@courses.route("/courses")
def get_courses():
    req = requests.get("%s/courses" % courses_url, headers=header)
    return req.json(), req.status_code


@courses.route("/courses/filter")
def get_filtered_courses():
    req = requests.get("%s/courses/filter" % courses_url, params=request.args.to_dict(), headers=header)

    return req.json(), req.status_code


@courses.route("/course/<course_id>", methods=["GET"])
def get_course(course_id):
    req = requests.get("%s/course/%s" % (courses_url, course_id), headers=header)
    return req.json(), req.status_code


@courses.route("/course/<course_id>", methods=["DELETE"])
@check_admin
def delete_course(course_id):
    req = requests.delete("%s/course/%s" % (courses_url, course_id), headers=header)
    return req.json(), req.status_code


@courses.route("/course/create", methods=["POST"])
@check_admin
def create_course():
    if request.is_json and request.data:
        req = requests.post("%s/course/create" % courses_url, json=request.json, headers=header)
        return req.json(), req.status_code

    return jsonify("JSON with fields is mandatory"), 400

@courses.route("/course/create/multi", methods=["POST"])
@check_admin
def create_course_multi():
    if request.is_json and request.data:
        req = requests.post("%s/course/create/multi" % courses_url, json=request.json, headers=header)
        return req.json(), req.status_code

    return jsonify("JSON with fields is mandatory"), 400
