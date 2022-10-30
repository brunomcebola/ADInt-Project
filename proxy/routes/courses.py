import os
import requests
from flask import Blueprint, request, jsonify

from proxy.middleware import *

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
def delete_course(course_id):
    req = requests.delete("%s/course/%s" % (courses_url, course_id), headers=header)
    return req.json(), req.status_code


@courses.route("/course/create", methods=["POST"])
def create_course():
    if request.is_json and request.data:
        req = requests.post("%s/course/create" % courses_url, json=request.json, headers=header)
        return req.json(), req.status_code

    return jsonify("JSON with fields is mandatory"), 400
