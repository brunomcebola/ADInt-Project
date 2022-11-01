import os
import yaml

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from middlewares import *


def format_activities_types(activities_types):

    activisties_types_list = []

    for activity_type, activities_sub_types in activities_types.items():
        for activity_sub_type, activity_db in activities_sub_types.items():
            activisties_types_list.append(
                {
                    "type_name": activity_type.strip().capitalize(),
                    "sub_type_name": activity_sub_type.strip().capitalize(),
                    "db": activity_db,
                }
            )

    return activisties_types_list


def store_activities_types(activities_types):
    for new_activity_type in activities_types:

        activity_type = (
            session.query(ActivityType)
            .filter(
                ActivityType.type_name == new_activity_type["type_name"],
                ActivityType.sub_type_name == new_activity_type["sub_type_name"],
            )
            .first()
        )

        if activity_type:
            continue

        activities_types = session.query(ActivityType.type_id, ActivityType.type_name)

        new_activity_type["type_id"] = len(set(activities_types)) + 1

        activity_type_exists = False
        for type in set(activities_types):
            if type[1] == new_activity_type["type_name"]:
                new_activity_type["type_id"] = type[0]
                activity_type_exists = True
                break

        new_activity_type["sub_type_id"] = 1

        if activity_type_exists:

            activities_sub_types = session.query(ActivityType.sub_type_id, ActivityType.sub_type_name).filter(
                ActivityType.type_id == new_activity_type["type_id"]
            )

            new_activity_type["sub_type_id"] = len(set(activities_sub_types)) + 1

        # Creating a new activity type and adding it to the database.
        activity_type = ActivityType()

        for key, value in new_activity_type.items():
            setattr(activity_type, key, value)

        session.add(activity_type)
    
    session.commit()


mandatory_params = [
    "HOST",
    "PORT",
    "DB_NAME",
]

load_dotenv()

for param in mandatory_params:
    if not os.getenv(param):
        raise SystemExit("[ENV] Parameter %s is mandatory" % param)

# read and validate configurations
config_file = "activities_list.yaml"

try:
    with open(config_file, "r") as stream:
        try:
            activities_types = yaml.safe_load(stream)

        except:
            raise SystemExit("Erro ao ler ficheiro de configurações (%s)." % config_file)
except:
    raise SystemExit("Ficheiro de configurações (%s) não encontrado." % config_file)


activities_types = format_activities_types(activities_types)

# create DB and table
Base = declarative_base()

# Declaration of data
class ActivityType(Base):
    __tablename__ = "activitiesTypes"
    type_id = Column(Integer, primary_key=True)
    type_name = Column(String)
    sub_type_id = Column(Integer, primary_key=True)
    sub_type_name = Column(String)
    db = Column(String, default=None)

    @classmethod
    def columns(cls):
        return [column.key for column in cls.__table__.columns]

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer)
    sub_type_id = Column(Integer)
    student_id = Column(Integer)
    start_time = Column(DateTime)
    stop_time = Column(DateTime)
    external_id = Column(Integer, default=0)
    description = Column(String, default="")

    @classmethod
    def columns(cls):
        return [column.key for column in cls.__table__.columns]

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


DATABASE_FILE = str(os.getenv("DB_NAME")).strip() + ".sqlite"

engine = create_engine("sqlite:///%s" % (DATABASE_FILE), echo=False)

Base.metadata.create_all(engine)  # Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()

store_activities_types(activities_types)

################################
########### FLASK ##############

app = Flask(__name__)


@app.before_request
def before_request():
    return check_auth_token()


# activities types


@app.route("/activities/types")
def get_activities_types():
    activities_types = session.query(ActivityType)

    return jsonify([activity_type.as_dict() for activity_type in activities_types]), 200


@app.route("/activity/type/<type_id>/<sub_type_id>")
def get_activity_db(type_id, sub_type_id):
    activity_type = session.query(ActivityType).get((type_id, sub_type_id))

    if activity_type:
        return jsonify(activity_type.as_dict()), 200

    return jsonify("Activity type not found"), 404


# activities


@app.route("/activities")
def get_activities():
    activities = session.query(Activity)

    return jsonify([activity.as_dict() for activity in activities]), 200


@app.route("/activities/filter")
def get_filtered_activities():
    filters = request.args.to_dict()
    allowed_filters = Activity.columns()

    for filter in filters:
        if filter not in allowed_filters:
            return jsonify("Filter not allowed (%s)" % filter), 400

    activities = session.query(Activity)
    for attr, value in filters.items():
        activities = activities.filter(getattr(Activity, attr).like("%%%s%%" % value))

    return jsonify([activity.as_dict() for activity in activities]), 200


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

        return jsonify("Successful deletion"), 200

    return jsonify("Not Found"), 404


@app.route("/activity/create", methods=["POST"])
@check_json
def create_activity():
    data = {}
    allowed_fields = Activity.columns()

    allowed_fields.remove("id")
    mandatory_fileds = [
        "type_id",
        "sub_type_id",
        "student_id",
        "start_time",
        "stop_time",
    ]

    for key in request.json:  # type: ignore
        if key in allowed_fields:
            data[key] = request.json[key]  # type: ignore
        else:
            return jsonify("Bad Request"), 400

    for field in mandatory_fileds:
        if field not in data:
            return jsonify("Bad Request"), 400

    activity_type = session.query(ActivityType).get((data["type_id"], data["sub_type_id"]))

    if activity_type:

        activity_type = activity_type.as_dict()

        if activity_type["is_external"] and "external_id" not in data:
            return jsonify("Bad Request"), 400
        elif not activity_type["is_external"] and "external_id" in data:
            del data["external_id"]

        try:
            data["start_time"] = datetime.strptime(data["start_time"], "%Y-%m-%dT%H:%M:%SZ")
            data["stop_time"] = datetime.strptime(data["stop_time"], "%Y-%m-%dT%H:%M:%SZ")
        except:
            return jsonify("Bad Request"), 400

        activity = Activity()

        for key, value in data.items():
            setattr(activity, key, value)

        session.add(activity)
        session.commit()

        return jsonify("Created"), 201

    return jsonify("Activity type does not exist"), 400


################################
############ MAIN ##############


if __name__ == "__main__":
    app.run(host=os.getenv("HOST"), port=int(str(os.getenv("PORT"))), debug=True)
