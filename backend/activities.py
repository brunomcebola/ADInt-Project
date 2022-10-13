from copy import deepcopy
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, jsonify
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from datetime import datetime

from aux_functions import *


def get_activity_info(activities, type_id, sub_type_id):
    for type in activities.values():
        if type["id"] == type_id:
            for sub_type in type["values"].values():
                if sub_type["id"] == sub_type_id:
                    info = deepcopy(sub_type)

                    del info["id"]

                    return info

    return {}


# TODO
def check_activities_format():
    return


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
    type_id = Column(Integer)
    sub_type_id = Column(Integer)
    student_id = Column(Integer)
    start_time = Column(DateTime)
    stop_time = Column(DateTime)  # TODO
    external_id = Column(Integer, default=0)
    description = Column(String, default="")

    @classmethod
    def columns(cls):
        columns = [column.key for column in cls.__table__.columns]

        columns.remove("id")

        return columns

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

    my_list = []
    for activity in activities:
        my_list.append(activity.as_dict())

    return jsonify(my_list), 200


@app.route("/activities/filter")
def get_filtered_activities():
    if request.args:
        filters = request.args.to_dict()
        allowed_filters = Activity.columns()

        for filter_key in filters:
            if filter_key not in allowed_filters:
                return jsonify("Bad Request"), 400

        activities = session.query(Activity)
        for attr, value in filters.items():
            activities = activities.filter(getattr(Activity, attr).like("%%%s%%" % value))

        my_list = []
        for activity in activities:
            my_list.append(activity.as_dict())

        return jsonify(my_list), 200
    return jsonify("Bad Request"), 400


@app.route("/activities/types")
def get_activities_types():
    return jsonify(configs["activities"]), 200


@app.route("/activity/type/<type_id>/<sub_type_id>/db")
def get_activity_db(type_id, sub_type_id):
    info = get_activity_info(configs["activities"], type_id, sub_type_id)

    if not info:
        return jsonify("Not Found"), 404

    if info["external"]:
        return jsonify(info["db"]), 200

    return jsonify(""), 200


@app.route("/activity/<activity_id>")
def get_activity(activity_id):
    activity = session.query(Activity).get(activity_id)

    if activity:
        return jsonify(activity.as_dict())

    return jsonify("Not Found"), 404


@app.route("/activity/<activity_id>", methods=["DELETE"])
def delete_activity(activity_id):
    activity = session.query(Activity).get(activity_id)

    if activity:
        session.delete(activity)
        session.commit()

        return jsonify("OK"), 200

    return jsonify("Not Found"), 404


@app.route("/activity/create", methods=["POST"])
def create_activity():
    if request.is_json and request.data:
        data = {}
        allowed_fields = Activity.columns()
        allowed_fields.remove("id")
        mandatory_fileds = ["type_id", "sub_type_id", "student_id", "start_time", "stop_time"]

        for key in request.json:  # type: ignore
            if key in allowed_fields:
                data[key] = request.json[key]  # type: ignore
            else:
                return jsonify("Bad Request"), 400

        for field in mandatory_fileds:
            if field not in data:
                return jsonify("Bad Request"), 400

        activity_info = get_activity_info(configs["activities"], data["type_id"], data["sub_type_id"])

        if activity_info:

            if activity_info["external"] and "external_id" not in data:
                return jsonify("Bad Request"), 400

            try:
                data["start_time"] = datetime.strptime(data["start_time"], "%Y-%m-%dT%H:%MZ")
                data["stop_time"] = datetime.strptime(data["stop_time"], "%Y-%m-%dT%H:%MZ")
            except:
                return jsonify("Bad Request"), 400

            activity = Activity()

            for key, value in data.items():
                setattr(activity, key, value)

            session.add(activity)
            session.commit()

            return jsonify("Created"), 201

        return jsonify("Bad Request"), 400

    return jsonify("Bad Request"), 400


@app.route("/activity/start", methods=["POST"])
def start_activity():
    if request.is_json and request.data:
        data = {}
        allowed_fields = ["type_id", "sub_type_id", "external_id", "description"]
        mandatory_fileds = ["type_id", "sub_type_id", "student_id"]

        for key in request.json:  # type: ignore
            if key in allowed_fields:
                data[key] = request.json[key]  # type: ignore
            else:
                return jsonify("Bad Request"), 400

        for field in mandatory_fileds:
            if field not in data:
                return jsonify("Bad Request"), 400

        activity_info = get_activity_info(configs["activities"], data["type_id"], data["sub_type_id"])

        if activity_info:

            if activity_info["external"] and "external_id" not in data:
                return jsonify("Bad Request"), 400

            data["start_time"] = datetime.now()

            activity = Activity()

            for key, value in data.items():
                setattr(activity, key, value)

            session.add(activity)
            session.commit()

            return jsonify("Created"), 201

        return jsonify("Bad Request"), 400

    return jsonify("Bad Request"), 400


@app.route("/activity/<activity_id>/stop", methods=["PUT"])
def stop_activity(activity_id):
    activity = session.query(Activity).get(activity_id)

    if getattr(activity, "stop_time"):
        return jsonify("Bad Request"), 400

    setattr(activity, "stop_time", datetime.now())

    session.commit()

    return jsonify("OK"), 200


################################
############ MAIN ##############


if __name__ == "__main__":
    app.run(host=configs["host"], port=configs["port"], debug=True)
