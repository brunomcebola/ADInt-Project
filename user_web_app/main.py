import os
import requests
import json

from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from oauthlib.oauth2 import WebApplicationClient
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

from middlewares import *

header = {"USER_TOKEN": "user"}

mandatory_params = [
    "HOST",
    "PORT",
    "PROXY_URL",
    "FENIX_CLIENT_ID",
    "FENIX_CLIENT_SECRET",
    "APP_SECRET",
]

load_dotenv()

proxy_url = os.getenv("PROXY_URL")

for param in mandatory_params:
    if not os.getenv(param):
        raise SystemExit("[ENV] Parameter %s is mandatory" % param)


app = Flask(__name__)

app.secret_key = os.getenv("APP_SECRET")

CORS(app)

# Backend

# Frontend

client = WebApplicationClient(os.getenv("FENIX_CLIENT_ID"))

Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    name = Column(String)
    courses = Column(String)


DATABASE_FILE = "UsersDB.sqlite"

engine = create_engine("sqlite:///%s?check_same_thread=False" % (DATABASE_FILE), echo=False)

Base.metadata.create_all(engine)  # Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect("/login-page")


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(user_id)


@app.errorhandler(requests.exceptions.ConnectionError)
def handle_bad_request(e):
    return redirect("/offline")

@app.route("/offline")
def offline():
    render_template("offline.html", base_url="https://127.0.0.1:8000")

@app.route("/<path:path>")
def catch_all():
    return redirect("/")


@app.route("/login")
def login():
    authorization_endpoint = "https://fenix.tecnico.ulisboa.pt/oauth/userdialog"
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri, code=302)


@app.route("/logout")
@login_required
def logout():
    session.delete(current_user)
    session.commit()
    logout_user()

    return redirect("/login-page")


@app.route("/login/callback")
def callback():
    code = request.args.get("code")

    token_endpoint = "https://fenix.tecnico.ulisboa.pt/oauth/access_token"

    token_url, headers, body = client.prepare_token_request(
        token_endpoint, authorization_response=request.url, redirect_url=request.base_url, code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(str(os.getenv("FENIX_CLIENT_ID")), str(os.getenv("FENIX_CLIENT_SECRET"))),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    course_endpoint = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person/courses?academicTerm=2022/2023"
    uri, headers, body = client.add_token(course_endpoint)
    course_info_response = requests.get(uri, headers=headers, data=body)

    user_courses = []
    # https://fenix.tecnico.ulisboa.pt/api/fenix/v1/courses/1610612925989
    for course in course_info_response.json().get("enrolments"):

        course_endpoint = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/courses/%s" % course["id"]
        uri, headers, body = client.add_token(course_endpoint)
        course_response = requests.get(uri, headers=headers, data=body)
        professor = course_response.json().get("teachers")[-1]["name"]

        # storing courses
        user_courses.append({"name":course["name"], "professor":professor, "school_year":course["academicTerm"][-9:]})

    # TODO: store in CoursesDB

    userinfo_endpoint = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person"
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    username = userinfo_response.json()["username"]
    name = userinfo_response.json()["name"]
    courses = json.dumps(user_courses)
    user = User(username=username, name=name, courses=courses)
    print("----------COURSES---------------")
    print(courses)
    req = requests.post("%s/course/create/multi" % proxy_url,json=courses, headers=header)
    if req.status_code != 201:
        return req.json(), req.status_code
    try:
        session.add(user)
        session.commit()
        # Login user in the session
        login_user(user)
    except:
        session.rollback()
        user = session.query(User).filter(User.username == username).first()
        login_user(user)
    return redirect("/")


@app.route("/")
@login_required
def home():
    return render_template("home.html", base_url="https://127.0.0.1:8001/api", user_id=current_user.__dict__["username"])


@app.route("/login-page")
def login_page():
    return render_template("login.html")


### API ###

@app.route("/api/activities/<user_id>")
def apiActivitiesFiler(user_id):
    req = requests.get("%s/activities/filter?student_id=%s" % (proxy_url, user_id ), headers=header)
    return req.json(), req.status_code

@app.route("/api/activities/types")
def apiActivitiesTypes():
    req = requests.get("%s/activities/types" % proxy_url, headers=header)  
    data =  req.json()

    # Search for external db's
    externals = []
    for activity in data:
        if activity["db"] != None:
            if activity["db"] not in externals:
                externals.append(activity["db"])

    for external in externals:
        if "Course" in external:
            course_req = requests.get("%s/db/%s" % (proxy_url,external), headers=header)

        if "PresentialServices" in external:
            presential_req = requests.get("%s/db/%s" % (proxy_url,external), headers=header)

    for activity in data:
        if activity["db"] != None:
            if "Course" in activity["db"]:
                activity["values"]= course_req.json()
            if "PresentialServices" in activity["db"]:
                activity["values"]= presential_req.json()
    return data, req.status_code

@app.route("/api/activity/create", methods=["POST"])
@check_json
def apiActivityCreate():
    req = requests.post("%s/activity/create" % proxy_url, json=request.json, headers=header)

    if req.status_code != 200:
        return req.json(), req.status_code

    return jsonify("Created"), 201 

@app.route("/api/evaluation/create", methods=["POST"])
@check_json
def apiActivityEvaluation():
    req = requests.post("%s/evaluation/create" % proxy_url, json=request.json, headers=header)

    if req.status_code != 200:
        return req.json(), req.status_code

    return jsonify("Created"), 201 

if __name__ == "__main__":
    app.run(host=os.getenv("HOST"), port=int(str(os.getenv("PORT"))), debug=True, ssl_context="adhoc")
