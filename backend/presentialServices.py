import json

from os import path
from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine

from auxFunctions import *

# read and validate configurations
general_configurations_file = "./config/general.yaml"
general_configurations = None

specific_configurations_file = "./config/presentialServices.yaml"
specific_configurations = None

general_configurations = read_yaml(general_configurations_file)
specific_configurations = read_yaml(specific_configurations_file)

validate_yaml(general_configurations, ["base_path"], general_configurations_file)
validate_yaml(specific_configurations, ["db_name"], specific_configurations_file)


# create DB and table
DATABASE_FILE = general_configurations["base_path"].rstrip("/") + "/" + specific_configurations["db_name"] + ".sqlite"

engine = create_engine("sqlite:///%s" % (DATABASE_FILE), connect_args={"check_same_thread": False}, echo=False)

Base = declarative_base()


class Presencial_Services(Base):
    __tablename__ = "presencial_services"
    id = Column(Integer, primary_key=True)
    name = Column(String)  # Name of the Service. Example: Bar de Civil
    description = Column(String)  # Desciption. Example: Sells food and drinks
    location = Column(String)  # Location of the Serice. Example: Civil's Building

    def __repr__(self):
        return "<Presencial_Services(id=%d name='%s', description='%s', location=%s)>" % (
            self.id,
            self.name,
            self.description,
            self.location,
        )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# functions to interact with the DB
def list_services():
    return session.query(Presencial_Services).all()


def create_service(name, description, location):
    service = Presencial_Services(name=name, description=description, location=location)
    session.add(service)
    session.commit()


################################
########### FLASK ##############

app = Flask(__name__)


@app.before_request
def before_request():
    return check_auth_token()


@app.route("/service/create", methods=["POST"])  # type: ignore
def createService():

    if request.json:
        info = {"name": None, "description": None, "location": None}

        for key in request.json:
            if key in info:
                info[key] = request.json[key]
            else: 
                return jsonify("Bad Request 1"), 400

        if None in info.values():
            return jsonify("Bad Request 2"), 400

        # create Service
        create_service(info["name"], info["description"], info["location"])

        return jsonify("Created"), 201

    return jsonify("Bad Request 3"), 400


@app.route("/services")
def getAllServices():
    myList = []

    services = list_services()

    for service in services:
        myList.append(service.as_dict())

    return json.dumps(myList)


################################
############ MAIN ##############


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=3000, debug=True)
