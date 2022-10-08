from email import message
from fileinput import filename
from multiprocessing import context
from operator import methodcaller
from flask import Flask, request, send_from_directory, redirect, url_for, render_template
from werkzeug.utils import secure_filename

import requests
import json

app = Flask(__name__)

# Services

@app.route('/createService', methods=['GET', 'POST'])
def createService():
    dicToSend = {"title":"doProxy", "description":"hello world", "location":"jerusalem"}
    req = requests.post('http://127.0.0.1:8000/createService',json=dicToSend )
    return req.json()

@app.route('/listServices')
def getAllServices():
    req = requests.request('GET', 'http://127.0.0.1:8000/listServices' )
    return req.json()

# Evaluations

@app.route('/createEvaluation', methods=['GET', 'POST'])
def createEvaluation():
    dicToSend = {"title":"doProxy", "description":"hello world", "location":"jerusalem"}
    req = requests.post('http://127.0.0.1:8003/createEvaluation',json=dicToSend )
    return req.json()

@app.route('/listEvaluation')
def getAllEvaluations():
    req = requests.request('GET', 'http://127.0.0.1:8003/listEvaluations' )
    return req.json()

# Courses

@app.route('/createCourse', methods=['GET', 'POST'])
def createCourse():
    dicToSend = {"title":"doProxy", "description":"hello world", "location":"jerusalem"}
    req = requests.post('http://127.0.0.1:8001/createCourse',json=dicToSend )
    return req.json()

@app.route('/listCourses')
def getAllCourses():
    req = requests.request('GET', 'http://127.0.0.1:8001/listCourses' )
    return req.json()

# Activities

@app.route('/createActivity', methods=['GET', 'POST'])
def createActivity():
    dicToSend = {"title":"doProxy", "description":"hello world", "location":"jerusalem"}
    req = requests.post('http://127.0.0.1:8002/createActivity',json=dicToSend )
    return req.json()

@app.route('/listActivities')
def getAllActivities():
    req = requests.request('GET', 'http://127.0.0.1:8002/listActivities' )
    return req.json()


################################
############ MAIN ##############


if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=8005, debug=True)