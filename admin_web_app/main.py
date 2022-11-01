import os
import re
import json
import requests

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect

header = {"ADMIN_TOKEN": "admin"}

mandatory_params = [
    "HOST",
    "PORT",
    "PROXY_URL"
]

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

    if not resp.json():
        return redirect("/services")

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
    resp = requests.get(
        "%s/activities/filter?type_id=2&sub_type_id=1&external_id=%s" % (proxy_url, course_id), headers=header
    )

    if resp.status_code >= 500:
        return redirect("/offline")

    activities = resp.json()

    if not activities:
        return redirect("/courses")

    resp = requests.get("%s/activities/types" % proxy_url, headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    activities_types_info = resp.json()

    for activity in activities:
        for type in activities_types_info:
            if activities_types_info[type]["id"] == activity["type_id"]:
                activity["type_name"] = type

                for sub_type in activities_types_info[type]["values"]:
                    if activities_types_info[type]["values"][sub_type]["id"] == activity["sub_type_id"]:
                        activity["sub_type_name"] = sub_type

        resp = requests.get(
            "%s/activity/type/%s/%s/db" % (proxy_url, activity["type_id"], activity["sub_type_id"]), headers=header
        )

        if resp.status_code >= 500:
            return redirect("/offline")

        if resp.json() == "CoursesDB":
            resp = requests.get("%s/course/%s" % (proxy_url, activity["external_id"]), headers=header)

            if resp.status_code >= 500:
                return redirect("/offline")

            activity["external_name"] = resp.json()["name"]

        elif resp.json() == "PresentialServicesDB":
            resp = requests.get("%s/service/%s" % (proxy_url, activity["external_id"]), headers=header)

            if resp.status_code >= 500:
                return redirect("/offline")

            activity["external_name"] = resp.json()["name"]

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
    if request.method == "GET":
        resp = requests.get("%s/activities" % proxy_url, headers=header)
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

        resp = requests.get("%s/activities/filter?%s" % (proxy_url, query), headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    activities = resp.json()

    resp = requests.get("%s/activities/types" % proxy_url, headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    activities_types_info = resp.json()

    activities_types = []
    activities_sub_types = []
    externals = []

    for activity in activities:
        for type in activities_types_info:
            if activities_types_info[type]["id"] == activity["type_id"]:
                activity["type_name"] = type

                if not re.search('"name": "%s"' % type, json.dumps(activities_types), re.M):
                    activities_types.append(
                        {
                            "name": type,
                            "value": activities_types_info[type]["id"],
                        }
                    )

                for sub_type in activities_types_info[type]["values"]:
                    if activities_types_info[type]["values"][sub_type]["id"] == activity["sub_type_id"]:
                        activity["sub_type_name"] = sub_type

                        if not re.search('"name": "%s"' % sub_type, json.dumps(activities_sub_types), re.M):
                            activities_sub_types.append(
                                {
                                    "name": sub_type,
                                    "value": activities_types_info[type]["values"][sub_type]["id"],
                                    "parent": activities_types_info[type]["id"],
                                }
                            )

        resp = requests.get(
            "%s/activity/type/%s/%s/db" % (proxy_url, activity["type_id"], activity["sub_type_id"]), headers=header
        )

        if resp.status_code >= 500:
            return redirect("/offline")

        if resp.json() == "CoursesDB":
            resp = requests.get("%s/course/%s" % (proxy_url, activity["external_id"]), headers=header)

            if resp.status_code >= 500:
                return redirect("/offline")

            activity["external_name"] = resp.json()["name"]

        elif resp.json() == "PresentialServicesDB":
            resp = requests.get("%s/service/%s" % (proxy_url, activity["external_id"]), headers=header)

            if resp.status_code >= 500:
                return redirect("/offline")

            activity["external_name"] = resp.json()["name"]

        if "external_name" in activity and not re.search(
            '"name": "%s"' % activity["external_name"], json.dumps(externals), re.M
        ):
            externals.append(
                {
                    "name": activity["external_name"],
                    "value": activity["external_id"],
                }
            )

    return render_template(
        "activities/list.html",
        show_filters=True,
        activities=activities,
        activities_types=activities_types,
        activities_sub_types=activities_sub_types,
        externals=externals,
        active_tab=5,
    )


@app.route("/activity/<activity_id>/delete")
def delete_activity(activity_id):
    resp = requests.delete("%s/activity/%s" % (proxy_url, activity_id), json=request.form, headers=header)

    if resp.status_code >= 500:
        return redirect("/offline")

    return redirect("/activities")


if __name__ == "__main__":
    app.run(host=os.getenv("HOST"), port=int(str(os.getenv("PORT"))), debug=True)
