import os
import requests


from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect

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


@app.route("/<path:path>")
def catch_all(path):
    return redirect("/")


@app.route("/")
def home():
    activities_types = [
        {"db": None, "sub_type_id": 1, "sub_type_name": "Sleep", "type_id": 1, "type_name": "Personal"},
        {"db": None, "sub_type_id": 2, "sub_type_name": "Eat", "type_id": 1, "type_name": "Personal"},
        {"db": None, "sub_type_id": 3, "sub_type_name": "Leisure", "type_id": 1, "type_name": "Personal"},
        {"db": None, "sub_type_id": 4, "sub_type_name": "Sports", "type_id": 1, "type_name": "Personal"},
        {"db": None, "sub_type_id": 5, "sub_type_name": "Other", "type_id": 1, "type_name": "Personal"},
        {
            "db": "PresentialServicesDB",
            "sub_type_id": 1,
            "sub_type_name": "Attend classes",
            "type_id": 2,
            "type_name": "Academic",
        },
        {"db": None, "sub_type_id": 2, "sub_type_name": "Study", "type_id": 2, "type_name": "Academic"},
        {
            "db": "PresentialServicesDB",
            "sub_type_id": 1,
            "sub_type_name": "Presential service",
            "type_id": 3,
            "type_name": "Administrative",
        },
    ]

    aux_dict = {}
    for activity_type in activities_types:
        if activity_type["type_name"] not in aux_dict:
            aux_dict[activity_type["type_name"]] = {"id": activity_type["type_id"], "options": []}

        aux_dict[activity_type["type_name"]]["options"].append(
            {"name": activity_type["sub_type_name"], "id": activity_type["sub_type_id"], "db": activity_type["db"]}
        )

    activities_types = aux_dict

    return render_template("home.html", activities_types=activities_types)


if __name__ == "__main__":
    app.run(host=os.getenv("HOST"), port=int(str(os.getenv("PORT"))), debug=True)
