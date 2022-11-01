# Python standard libraries
import code
import json
import os
import sys

# Third-party libraries
from flask import Flask, redirect, request, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user

from oauthlib.oauth2 import WebApplicationClient
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

FENIX_CLIENT_ID = 1132965128044859
FENIX_CLIENT_SECRET = "B32S8fLKE3jtnYdwkjSJMvhG55WwZQIXnaUbRmA4Mr4bAn3uour7VgqS7py/wYhP0BK+6VefLj2a7FDj7FsOYQ=="


# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///multi.db"
db = SQLAlchemy()

# DB "cache"
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)
    name = db.Column(db.String(256), unique=True)
    email = db.Column(db.String(256), unique=True)
    courses = db.Column(db.String(512), unique=True)

# User session management setup
login_manager = LoginManager()
login_manager.init_app(app)

# OAuth 2 client setup
client = WebApplicationClient(FENIX_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    if current_user.is_authenticated:
        #TODO: INSERT HOMEPAGE
        print(current_user.courses)
        return (
            "<p>Hello, {} - {}! You're , headers=headerlogged in! Email: {}</p>"
            '<a class="button" href="/logout">Logout</a>'
            '<p> <a href="/private_page">page requiring authentication</a></p>'.format(
                current_user.name, current_user.username, current_user.email, current_user.id
            )
        )
    else:
        #TODO: INSERT LOGIN PAGE
        return ('<p> <a href="/private_page">page requiring authentication</a></p>'
            '<a class="button" href="/login">Login Via Fenix</a>')


@app.route("/login")
def login():
    authorization_endpoint = "https://fenix.tecnico.ulisboa.pt/oauth/userdialog"
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    code = request.args.get("code")

    token_endpoint = "https://fenix.tecnico.ulisboa.pt/oauth/access_token"

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(FENIX_CLIENT_ID, FENIX_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    course_endpoint = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person/courses?academicTerm=2022/2023"
    uri, headers, body = client.add_token(course_endpoint)
    course_info_response = requests.get(uri, headers=headers, data=body)

    user_courses = []

    for course in course_info_response.json().get("enrolments"):
        user_courses.append(course["name"])

    userinfo_endpoint = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person"
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)


    if userinfo_response.json().get("email"):
        username = userinfo_response.json()["username"]
        email = userinfo_response.json()["email"]
        name = userinfo_response.json()["name"]
        courses = json.dumps(user_courses)
        user = User(username = username,email = email,name=name, courses=courses)

        try:
            db.session.add(user)
            db.session.commit()
            # Login user in the session
            login_user(user)
        except:
            db.session.rollback()
            user = db.session.query(User).filter(User.username == username).first()
            login_user(user)
        return redirect(url_for("index"))
    else:
        return "User email not available.", 400

@app.route("/private_page")
def private_page():
    return "private page hehe"

@app.route("/logout")
@login_required
def logout():
    # Logout the user of the sessions
    logout_user()
    return redirect(url_for("index"))
    
# hook up extensions to app
db.init_app(app)

if __name__ == "__main__":
    if "--setup" in sys.argv:
        with app.app_context():
            db.create_all()
            db.session.commit()
            print("Database tables created")
    else:
        app.run(debug=True, ssl_context="adhoc")