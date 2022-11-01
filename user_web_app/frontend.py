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
    return render_template("home.html", active_tab=1)


if __name__ == "__main__":
    app.run(host=os.getenv("HOST"), port=int(str(os.getenv("PORT"))), debug=True)
