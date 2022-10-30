import os
import requests
from flask import Flask, jsonify
from dotenv import load_dotenv

from proxy.middleware import *

from routes.courses import courses
from routes.activities import activities
from routes.evaluations import evaluations
from routes.presential_services import presential_services

load_dotenv()

mandatory_params = [
    "PROXY_HOST",
    "PROXY_PORT",
    "TOKEN",
    "COURSES_URL",
    "ACTIVITIES_URL",
    "EVALUATIONS_URL",
    "PRESENTIAL_SERVICES_URL",
]

for param in mandatory_params:
    if not os.getenv(param):
        raise SystemExit("[ENV] Parameter %s is mandatory" % param)

app = Flask(__name__)

app.register_blueprint(courses)
app.register_blueprint(activities)
app.register_blueprint(evaluations)
app.register_blueprint(presential_services)


@app.errorhandler(requests.exceptions.ConnectionError)
def handle_bad_request(e):
    return jsonify("Bad Gateway"), 502


if __name__ == "__main__":
    app.run(host=os.getenv("PROXY_HOST"), port=int(str(os.getenv("PROXY_PORT"))), debug=True)
