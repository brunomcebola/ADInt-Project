from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import requests

from aux_functions import *


# read and validate configurations
config_file = "./config.yaml"

configs = read_yaml(config_file)

validate_yaml(configs, ["host", "port", "proxy_host", "proxy_port"], config_file)

proxy_url = "http://%s:%s" % (configs["proxy_host"], configs["proxy_port"])

app = Flask(__name__)


@app.errorhandler(requests.exceptions.ConnectionError)
def handle_bad_request(e):
    return redirect("/offline")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/offline")
def offline():
    return render_template("offline.html")


# Services


@app.route("/services")
def get_services():
    resp = requests.get("%s/services" % proxy_url)

    if resp.status_code >= 500:
        return redirect("/offline")

    return render_template("services/list.html", services=resp.json())


@app.route("/service/<service_id>/evaluations")
def get_service_evaluations(service_id):
    resp = requests.get("%s/service/%s/evaluations" % (proxy_url, service_id))

    if resp.status_code >= 500:
        return redirect("/offline")

    return render_template("evaluations/list.html", evaluations=resp.json())


@app.route("/service/<service_id>/delete")
def delete_service(service_id):
    resp = requests.delete("%s/service/%s" % (proxy_url, service_id), json=request.form)

    if resp.status_code >= 500:
        return redirect("/offline")

    return redirect(request.referrer)


@app.route("/service/create", methods=["GET", "POST"])
def create_service():
    if request.method == "POST":
        resp = requests.post("%s/service/create" % proxy_url, json=request.form)

        if resp.status_code >= 500:
            return redirect("/offline")

        return redirect("/services")
    else:
        return render_template("services/create.html")


# Evaluations


@app.route("/evaluation/<evaluation_id>/delete")
def delete_evaluation(evaluation_id):
    resp = requests.delete("%s/evaluation/%s" % (proxy_url, evaluation_id), json=request.form)

    if resp.status_code >= 500:
        return redirect("/offline")

    return redirect(request.referrer)


# Courses


@app.route("/courses")
def get_courses():
    resp = requests.get("%s/courses" % proxy_url)

    if resp.status_code >= 500:
        return redirect("/offline")

    return render_template("courses/list.html", courses=resp.json())


@app.route("/course/<course_id>/delete")
def delete_course(course_id):
    resp = requests.delete("%s/course/%s" % (proxy_url, course_id), json=request.form)

    if resp.status_code >= 500:
        return redirect("/offline")

    return redirect(request.referrer)


@app.route("/course/create", methods=["GET", "POST"])
def create_course():
    if request.method == "POST":
        resp = requests.post("%s/course/create" % proxy_url, json=request.form)

        if resp.status_code >= 500:
            return redirect("/offline")

        return redirect("/courses")
    else:
        return render_template("courses/create.html")


# @app.route("/course/<course_id>/attendances")
# def get_course_attendances(course_id):
#     resp = requests.get("%s/activities/filter?type_id=2&sub_type_id=1&external_id=%s" % (proxy_url, course_id))

#     if resp.status_code >= 500:
#         return redirect("/offline")

#     return render_template("activities/list.html", activities=resp.json())


# Activities


@app.route("/activities", methods=["GET", "POST"])
def get_activities():
    if request.method == "GET":
        resp = requests.get("%s/activities" % proxy_url)
    else:
        query = ""

        if "filter_type" in request.form:
            query = query + "type_id=" + request.form["type_id"] + "&"

        if "filter_sub_type" in request.form:
            query = query + "sub_type_id=" + request.form["sub_type_id"] + "&"

        if "filter_external" in request.form:
            query = query + "external_id=" + request.form["external_id"] + "&"

        if "filter_student" in request.form:
            query = query + "student_id=" + request.form["student_id"] + "&"

        print("%s/activities/filter?%s" % (proxy_url, query))

        resp = requests.get("%s/activities/filter?%s" % (proxy_url, query))

    if resp.status_code >= 500:
        return redirect("/offline")

    activities = resp.json()
    
    print(activities)

    resp = requests.get("%s/activities/types" % proxy_url)

    if resp.status_code >= 500:
        return redirect("/offline")

    activities_types_info = resp.json()

    activities_types = []
    activities_sub_types = []

    for type in activities_types_info:
        activities_types.append({"name": type, "value": activities_types_info[type]["id"]})
        for sub_type in activities_types_info[type]["values"]:
            activities_sub_types.append(
                {
                    "name": sub_type,
                    "value": activities_types_info[type]["values"][sub_type]["id"],
                    "parent": activities_types_info[type]["id"],
                }
            )

    for activity in activities:
        for type in activities_types:
            if type["value"] == activity["type_id"]:
                activity["type_name"] = type["name"]

        for sub_type in activities_sub_types:
            if sub_type["value"] == activity["sub_type_id"] and sub_type["parent"] == activity["type_id"]:
                activity["sub_type_name"] = sub_type["name"]

    return render_template(
        "activities/list.html",
        activities=activities,
        activities_types=activities_types,
        activities_sub_types=activities_sub_types,
    )


if __name__ == "__main__":
    app.run(host=configs["host"], port=configs["port"], debug=True)
