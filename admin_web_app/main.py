import os
import re
import json
import requests

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect

header = {"Authorization": "admin"}

mandatory_params = ["HOST", "PORT", "PROXY_URL"]

load_dotenv()

for param in mandatory_params:
    if not os.getenv(param):
        raise SystemExit("[ENV] Parameter %s is mandatory" % param)


proxy_url = os.getenv("PROXY_URL")

app = Flask(__name__)


@app.errorhandler(requests.exceptions.ConnectionError)
def handle_bad_request(e):
    return redirect("/offline")


@app.route("/")
def home():
    return render_template("home.html", active_tab=1)


@app.route("/offline")
def offline():
    return render_template("offline.html")


@app.route("/<path:path>")
def catch_all(path):
    return redirect("/")


# Services


@app.route("/services")
def get_services():
    resp = requests.get("%s/services" % proxy_url, headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    return render_template("services/list.html", services=resp.json(), active_tab=2)


@app.route("/service/<service_id>/evaluations")
def get_service_evaluations(service_id):
    resp = requests.get("%s/service/%s/evaluations" % (proxy_url, service_id), headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    return render_template("evaluations/list.html", evaluations=resp.json())


@app.route("/service/<service_id>/delete")
def delete_service(service_id):
    resp = requests.delete("%s/service/%s" % (proxy_url, service_id), json=request.form, headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    return redirect("/services")


@app.route("/service/create", methods=["GET", "POST"])
def create_service():
    if request.method == "POST":
        resp = requests.post("%s/service/create" % proxy_url, json=request.form, headers=header)

        if resp.status_code >= 500:
            return redirect("/offline")

        return redirect("/services")
    else:
        return render_template("services/create.html")


# Courses


@app.route("/courses")
def get_courses():
    resp = requests.get("%s/courses" % proxy_url, headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    return render_template("courses/list.html", courses=resp.json(), active_tab=3)


@app.route("/course/<course_id>/delete")
def delete_course(course_id):
    resp = requests.delete("%s/course/%s" % (proxy_url, course_id), json=request.form, headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    return redirect("/courses")


@app.route("/course/create", methods=["GET", "POST"])
def create_course():
    if request.method == "POST":
        resp = requests.post("%s/course/create" % proxy_url, json=request.form, headers=header)

        if resp.status_code >= 500:
            return redirect("/offline")

        return redirect("/courses")
    else:
        return render_template("courses/create.html")


@app.route("/course/<course_id>/attendances")
def get_course_attendances(course_id):
    resp = requests.get("%s/activities/filter?activity_id=6&external_id=%s" % (proxy_url, course_id), headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    activities = resp.json()

    resp = requests.get("%s/courses" % (proxy_url), headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    courses = resp.json()

    for activity in activities:
        for course in courses:
            if course["id"] == activity["external_id"]:
                activity["external_name"] = course["name"]

    return render_template(
        "activities/list.html",
        activities=activities,
    )


# Evaluations


@app.route("/evaluations")
def get_evaluations():
    resp = requests.get("%s/evaluations" % proxy_url, headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    return render_template("evaluations/list.html", evaluations=resp.json(), active_tab=4)


@app.route("/evaluation/<evaluation_id>/delete")
def delete_evaluation(evaluation_id):
    resp = requests.delete("%s/evaluation/%s" % (proxy_url, evaluation_id), json=request.form, headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    return redirect("/evaluations")


# Activities


@app.route("/activities", methods=["GET", "POST"])
def get_activities():
    print(request.form)

    if request.method == "GET":
        resp = requests.get("%s/activities" % proxy_url, headers=header)
    else:
        query = ""

        for f in request.form:
            if request.form[f]:
                query += f + "=" + request.form[f] + "&"

        resp = requests.get("%s/activities/filter?%s" % (proxy_url, query), headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    activities = resp.json()

    resp = requests.get("%s/activities/types" % proxy_url, headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    activities_types = resp.json()

    # Search for external db's
    externals = []
    for activity_type in activities_types:
        if activity_type["db"] and activity_type["db"] not in externals:
            externals.append({"name": activity_type["db"], "values": []})

    for external in externals:
        req = requests.get("%s/db/%s" % (proxy_url, external["name"]), headers=header)

        if req.status_code == 200:
            external["values"] = req.json()

    for activity_type in activities_types:
        if activity_type["db"]:
            for external in externals:
                if activity_type["db"] == external["name"]:
                    activity_type["values"] = external["values"]

    for activity in activities:
        for activity_type in activities_types:
            if activity_type["id"] == activity["activity_id"] and activity_type["db"]:
                for value in activity_type["values"]:
                    if value["id"] == activity["external_id"]:
                        activity["external_name"] = value["name"]

    students = []
    externals = []
    activities_types = []
    for activity in activities:
        if activity["student_id"] not in students:
            students.append(activity["student_id"])

        exists = False
        for activity_type in activities_types:
            if activity_type["id"] == activity["activity_id"]:
                exists = True

        if not exists:
            activities_types.append(
                {"id": activity["activity_id"], "name": activity["type_name"] + " - " + activity["activity_name"]}
            )

        if activity["external_id"]:
            exists = False
            for external in externals:
                if external["id"] == activity["external_id"]:
                    exists = True

            if not exists:
                externals.append({"id": activity["external_id"], "name": activity["external_name"]})

    if request.method == "GET":
        c_student = None
        c_external = None
        c_activity = None
    else:
        c_student = request.form["student_id"]
        c_external = request.form["external_id"]
        c_activity = request.form["activity_id"]

    return render_template(
        "activities/list.html",
        active_tab=5,
        show_filters=True,
        activities=activities,
        students=students,
        externals=externals,
        activities_types=activities_types,
        c_student=c_student,
        c_external=c_external,
        c_activity=c_activity,
    )


@app.route("/activity/<activity_id>/delete")
def delete_activity(activity_id):
    resp = requests.delete("%s/activity/%s" % (proxy_url, activity_id), json=request.form, headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    return redirect("/activities")


if __name__ == "__main__":
    app.run(host=os.getenv("HOST"), port=int(str(os.getenv("PORT"))), debug=True)
