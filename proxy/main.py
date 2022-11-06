import os
import requests
from flask import Flask, jsonify
from dotenv import load_dotenv

from middlewares import *

from routes.courses import courses
from routes.activities import activities
from routes.evaluations import evaluations
from routes.presential_services import presential_services


mandatory_params = [
    "HOST",
    "PORT",
    "TOKEN",
    "COURSES_URL",
    "ACTIVITIES_URL",
    "EVALUATIONS_URL",
    "PRESENTIAL_SERVICES_URL",
]

load_dotenv()

header = {"Token": str(os.getenv("TOKEN"))}

courses_url = os.getenv("COURSES_URL")
presential_services_url = os.getenv("PRESENTIAL_SERVICES_URL")

for param in mandatory_params:
    if not os.getenv(param):
        raise SystemExit("[ENV] Parameter %s is mandatory" % param)

app = Flask(__name__)

app.register_blueprint(courses)
app.register_blueprint(activities)
app.register_blueprint(evaluations)
app.register_blueprint(presential_services)

@app.before_request
def before_request():
    return check_permission()

@app.errorhandler(requests.exceptions.ConnectionError)
def handle_bad_request(e):
    return jsonify("Bad Gateway"), 502

@courses.route("/db/<db_name>", methods=["GET"])
def get_course(db_name):
    if "Course" in db_name:
        req = requests.get("%s/courses" % courses_url, headers=header)
    if "PresentialService" in db_name:
        req = requests.get("%s/services" % presential_services_url, headers=header)
    return req.json(), req.status_code


if __name__ == "__main__":
    app.run(host=os.getenv("HOST"), port=int(str(os.getenv("PORT"))), debug=True)
