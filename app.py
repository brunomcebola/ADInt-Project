# Python standard libraries
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


# Credentials of Fenix APP
FENIX_CLIENT_ID = 1132965128044859
FENIX_CLIENT_SECRET = "B32S8fLKE3jtnYdwkjSJMvhG55WwZQIXnaUbRmA4Mr4bAn3uour7VgqS7py/wYhP0BK+6VefLj2a7FDj7FsOYQ=="


# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# DB for "cache" ?
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///multi.db"
db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)
    name = db.Column(db.String(256), unique=True)
    email = db.Column(db.String(256), unique=True)


# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# OAuth 2 client setup
client = WebApplicationClient(FENIX_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User Pre-Login Page
@app.route("/")
def index():
    if current_user.is_authenticated:
        return (
            "<p>Hello, {} - {}! You're logged in! Email: {}</p>"
            '<a class="button" href="/logout">Logout</a>'
            '<p> <a href="/private_page">page requiring authentication</a></p>'.format(
                current_user.name, current_user.username, current_user.email
            )
        )
    else:
        return ('<p> <a href="/private_page">page requiring authentication</a></p>'
            '<a class="button" href="/login">Login Via Fenix</a>')

# Login in Fenix
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
        redirect_url=request.base_url, # where we want to go after the login
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(FENIX_CLIENT_ID, FENIX_CLIENT_SECRET),
    )
    
    # Basically implying that we will always use the token
    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person"
    uri, headers, body = client.add_token(userinfo_endpoint) # "Generate" the token ?

    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email"):
        username = userinfo_response.json()["username"]
        email = userinfo_response.json()["email"]
        name = userinfo_response.json()["name"]
        user = User(username = username,email = email,name=name)

        try:
            db.session.add(user)
            db.session.commit()
            # Login the user in this session
            login_user(user)
        except:
            db.session.rollback()
            user = db.session.query(User).filter(User.username == username).first()
            login_user(user)
        return redirect(url_for("index"))
    else:
        return "User email not available.", 400


@app.route("/logout")
@login_required
def logout():
    #Logout of the session
    logout_user()
    return redirect(url_for("index"))

# We put our Home Page Here
@app.route("/private_page")
@login_required
def lprivate_page():
    return "private page"
    
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