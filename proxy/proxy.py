from email import message
from fileinput import filename
from multiprocessing import context
from operator import methodcaller
from flask import Flask, request, jsonify, redirect, url_for, render_template
from werkzeug.utils import secure_filename

import requests
import json

header = {"Token": "proxy"}

app = Flask(__name__)

# Services


@app.route("/createService", methods=["POST"])
def createService():
    req = requests.post("http://127.0.0.1:3000/createService", json=request.json, headers=header)
    return req.json()


@app.route("/listServices")
def getAllServices():
    req = requests.get("http://127.0.0.1:3000/listServices", headers=header)
    return req.json()


# Evaluations


@app.route("/createEvaluation", methods=["POST"])
def createEvaluation():
    if request.json:
        services = requests.get("http://127.0.0.1:3000/listServices", headers=header)
        eval = request.json
        for service in services.json():

            if str(service['id']) == str(eval['serviceID']):
                if eval['rating'] < 1 or eval['rating'] > 5:
                    return "Bad request, Invalid input, that rating is not possible", 400
                req = requests.post("http://127.0.0.1:8003/createEvaluation", json=request.json, headers=header)
                return req.json(), req.status_code
        return "Service does not exist", 406

    return "Bad Request", 400


@app.route("/listEvaluations")
def getAllEvaluations():
    req = requests.get("http://127.0.0.1:8003/listEvaluations", headers=header)
    return req.json()

@app.route("/listEvaluations/<serviceID>")
def getEvaluationsService(serviceID):
    req = requests.get("http://127.0.0.1:8003/listEvaluations", headers=header)

    evaluations = []
    
    for evaluation in req.json():
        if str(evaluation['serviceID']) == serviceID:
            print(evaluation['serviceID'])
            evaluations.append(evaluation)
    return jsonify(evaluations)

# Courses


@app.route("/createCourse", methods=["GET", "POST"])
def createCourse():
    dicToSend = {"title": "doProxy", "description": "hello world", "location": "jerusalem"}
    req = requests.post("http://127.0.0.1:8001/createCourse", json=dicToSend, headers=header)
    return req.json()


@app.route("/listCourses")
def getAllCourses():
    req = requests.get("http://127.0.0.1:8001/listCourses", headers=header)
    return req.json()


# Activities


@app.route("/createActivity", methods=["GET", "POST"])
def createActivity():
    dicToSend = {"title": "doProxy", "description": "hello world", "location": "jerusalem"}
    req = requests.post("http://127.0.0.1:8002/createActivity", json=dicToSend, headers=header)
    return req.json()


@app.route("/listActivities")
def getAllActivities():
    req = requests.get("http://127.0.0.1:8002/listActivities")
    return req.json()


################################
############ MAIN ##############


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
