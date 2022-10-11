from email import message
from fileinput import filename
from flask import Flask, request, send_from_directory, redirect, url_for, jsonify
from werkzeug.utils import secure_filename

from http import HTTPStatus


import requests
import json

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

from sqlalchemy import inspect

import json
import datetime
from sqlalchemy.orm import sessionmaker
from os import path

from auxFunctions import *


def get_response(code):
    return jsonify(code.phrase), code.value


# SLQ access layer initialization
DATABASE_FILE = "./Databases/EvaluationDB.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t WARNING: DATABASE ALREADY EXISTS ")

engine = create_engine("sqlite:///%s" % (DATABASE_FILE), echo=False)  # echo = True shows all SQL calls

Base = declarative_base()

# Declaration of data
class Evaluation(Base):
    __tablename__ = "evaluation"
    id = Column(Integer, primary_key=True)
    serviceID = Column(Integer)
    rating = Column(Integer)

    def __repr__(self):
        return "<Evaluation(id=%d title='%s', rating='%s')>" % (self.id, self.title, self.rating)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


Base.metadata.create_all(engine)  # Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()


def listEvaluations():
    return session.query(Evaluation).all()


def newEvaluation(serviceID, rating):
    eval = Evaluation(serviceID=serviceID, rating=rating)
    session.add(eval)
    session.commit()


################################
########### FLASK ##############

app = Flask(__name__)


@app.before_request
def before_request():
    return check_auth_token()


@app.route("/createEvaluation", methods=["POST"])  # type: ignore
def createEvaluations():

    if request.json:
        info = {"serviceID": None, "rating": None}

        for key in request.json:
            info[key] = request.json[key]

        if None in info.values():
            return get_response(HTTPStatus.BAD_REQUEST)

        # create Service
        newEvaluation(info["serviceID"], info["rating"])

        return get_response(HTTPStatus.CREATED)

    return get_response(HTTPStatus.BAD_REQUEST)


@app.route("/listEvaluations")
def getAllEvaluations():
    if "Token" in request.headers:
        if request.headers["Token"] == "proxy":
            myList = []

            evaluations = listEvaluations()

            for evaluation in evaluations:
                myList.append(evaluation.as_dict())

            return myList
        return get_response(HTTPStatus.UNAUTHORIZED)
    return get_response(HTTPStatus.PROXY_AUTHENTICATION_REQUIRED)


################################
############ MAIN ##############


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8003, debug=True)
