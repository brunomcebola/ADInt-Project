from sqlalchemy.orm import sessionmaker
from flask import Flask, request, jsonify
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from datetime import datetime

from aux_functions import *

# read and validate configurations
config_file = "./config/activities.yaml"

configs = read_yaml(config_file)

validate_yaml(configs, ["db_path", "db_name", "host", "port", "activities"], config_file)

# create DB and table
Base = declarative_base()

# Declaration of data
class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)
    name = Column(String)  # Name of the Activity. Example: Aplicações Distribuidas da Internet
    type = Column(String)  # Activity Type. Example: Aula/Serviço
    external_id = Column(Integer, default=0)
    description = Column(String)  # Desciption. Example: Learning REST API
    start_time = Column(DateTime)  # Year. Example: 3-2-2022
    stop_time = Column(DateTime)

    def __repr__(self):
        return "<Activities(id=%d name='%s', type='%s', time='%s', description='%s', start_time='%s', stop_time='%s')>" % (
            self.id,
            self.name,
            self.type,
            self.description,
            str(self.start_time),
            str(self.stop_time),
        )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


DATABASE_FILE = configs["db_path"].rstrip("/") + "/" + configs["db_name"] + ".sqlite"

engine = create_engine("sqlite:///%s" % (DATABASE_FILE), echo=False)

Base.metadata.create_all(engine)  # Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()


################################
########### FLASK ##############

app = Flask(__name__)


@app.before_request
def before_request():
    return check_auth_token()


@app.route("/activities")
def get_activities():
    activities = session.query(Activity).all()

    myList = []
    for activity in activities:
        myList.append(activity.as_dict())

    return myList


@app.route("/activities/types")
def get_activities_types():
    return jsonify(configs["activities"]), 200


@app.route("/activity/<activity_id>", methods=["GET", "DELETE"])
def get_and_delete_activity(activity_id):
    if request.method == "GET":
        activity = session.query(Activity).get(activity_id)

        if activity:
            return jsonify(activity.as_dict())

        return jsonify("Not Found"), 404

    else:
        activity = session.query(Activity).get(activity_id)
        session.delete(activity)
        session.commit()

        return jsonify("OK"), 200


@app.route("/activity/create", methods=["POST"])
def create_activity():
    if request.is_json and request.data:
        info = {"name": None, "type": None, "external_id": None, "description": None, "start_time": None, "stop_time": None}

        for key in request.json:  # type: ignore
            if key in info:
                info[key] = request.json[key]  # type: ignore
            else:
                return jsonify("Bad Request"), 400

        if None in info.values():
            return jsonify("Bad Request"), 400

        # TODO: check if activity type exists

        if configs["activities"][info["type"]][info["name"]]["external"]:
            course = Activity(
                name=info["name"],
                type=info["type"],
                external_id=info["external_id"],
                description=info["description"],
                start_time=datetime.strptime(info["start_time"], "%Y-%m-%dT%H:%MZ"),  # type: ignore
                stop_time=datetime.strptime(info["stop_time"], "%Y-%m-%dT%H:%MZ"),  # type: ignore
            )
        else:
            course = Activity(
                name=info["name"],
                type=info["type"],
                description=info["description"],
                start_time=datetime.strptime(info["start_time"], "%Y-%m-%dT%H:%MZ"),  # type: ignore
                stop_time=datetime.strptime(info["stop_time"], "%Y-%m-%dT%H:%MZ"),  # type: ignore
            )

        session.add(course)
        session.commit()

        return jsonify("Created"), 201

    return jsonify("Bad Request"), 400


@app.route("/activity/start", methods=["POST"])
def start_activity():
    if request.is_json and request.data:
        info = {"name": None, "type": None, "external_id": None, "description": None}

        for key in request.json:  # type: ignore
            if key in info:
                info[key] = request.json[key]  # type: ignore
            else:
                return jsonify("Bad Request"), 400

        if None in info.values():
            return jsonify("Bad Request"), 400

        # TODO: check if activity type exists

        if configs["activities"][info["type"]][info["name"]]["external"]:
            course = Activity(
                name=info["name"],
                type=info["type"],
                external_id=info["external_id"],
                description=info["description"],
                start_time=datetime.now(),  # type: ignore
            )
        else:
            course = Activity(
                name=info["name"],
                type=info["type"],
                description=info["description"],
                start_time=datetime.now(),  # type: ignore
            )

        session.add(course)
        session.commit()

        return jsonify("Created"), 201

    return jsonify("Bad Request"), 400


@app.route("/activity/<activity_id>/stop", methods=["PUT"])
def stop_activity(activity_id):
    activity = session.query(Activity).get(activity_id)

    setattr(activity, "stop_time", datetime.now())

    session.commit()

    return "OK", 200


################################
############ MAIN ##############


if __name__ == "__main__":
    app.run(host=configs["host"], port=configs["port"], debug=True)
