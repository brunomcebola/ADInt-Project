from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import requests

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("mainPage.html", message="Home page")


@app.route("/services")
def services():
    services = requests.get("http://127.0.0.1:5000/listServices").json()

    return render_template("listServices.html", services=services)


@app.route("/service/create", methods=["GET", "POST"])
def createService():
    if request.method == "POST":
        response = requests.post("http://127.0.0.1:5000/createService", json=request.form).json()

        return "Serviço criado com sucesso"
    else:
        return render_template("createService.html")


@app.route("/service/<path:serviceID>/evaluations")
def serviceEvaluations(serviceID):
    return serviceID


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
