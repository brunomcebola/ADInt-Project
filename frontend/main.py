from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import requests

from auxFunctions import *

# read and validate configurations
config_file = "./config.yaml"

configs = read_yaml(config_file)

validate_yaml(configs, ["host", "port", "proxy_host", "proxy_port"], config_file)


proxy_url = "http://%s:%s" % (configs["proxy_host"], configs["proxy_port"])

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("home.html", message="Home page")


# Services


@app.route("/services")
def services():
    services = requests.get("%s/services" % proxy_url).json()
    return render_template("services/list.html", services=services)


@app.route("/service/<service_id>/evaluations")
def serviceEvaluations(service_id):
    evaluations = requests.get("%s/service/%s/evaluations" % (proxy_url, service_id)).json()

    return render_template("evaluations/list.html", evaluations=evaluations)


@app.route("/service/<service_id>/delete")
def delete_service(service_id):
    requests.delete("%s/service/%s" % (proxy_url, service_id), json=request.form)

    return redirect(request.referrer)


@app.route("/service/create", methods=["GET", "POST"])
def createService():
    if request.method == "POST":
        requests.post("%s/service/create" % proxy_url, json=request.form)

        return redirect("/services")
    else:
        return render_template("services/create.html")


# Evaluations


@app.route("/evaluation/<evaluation_id>/delete")
def delete_evaluation(evaluation_id):
    requests.delete("%s/evaluation/%s" % (proxy_url, evaluation_id), json=request.form)

    return redirect(request.referrer)


if __name__ == "__main__":
    app.run(host=configs["host"], port=configs["port"], debug=True)
