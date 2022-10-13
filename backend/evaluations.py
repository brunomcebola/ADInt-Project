from datetime import datetime
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, jsonify
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime

from aux_functions import *

# read and validate configurations
config_file = "./config/evaluations.yaml"

configs = read_yaml(config_file)

validate_yaml(configs, ["db_path", "db_name", "host", "port"], config_file)

# create DB and table
Base = declarative_base()


class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer)
    rating = Column(Integer)
    description = Column(String)
    datetime = Column(DateTime)

    @classmethod
    def columns(cls):
        return [column.key for column in cls.__table__.columns]

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


DATABASE_FILE = configs["db_path"].rstrip("/") + "/" + configs["db_name"] + ".sqlite"

engine = create_engine("sqlite:///%s" % (DATABASE_FILE), echo=False)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


################################
########### FLASK ##############

app = Flask(__name__)


@app.before_request
def before_request():
    return check_auth_token()


@app.route("/evaluations")
def get_evaluations():
    evaluations = session.query(Evaluation).all()

    myList = []
    for evaluation in evaluations:
        myList.append(evaluation.as_dict())

    return jsonify(myList)


@app.route("/evaluation/<evaluation_id>")
def get_evaluation(evaluation_id):

    evaluation = session.query(Evaluation).get(evaluation_id)

    if evaluation:
        return jsonify(evaluation.as_dict())

    return jsonify("Not Found"), 404


@app.route("/evaluation/<evaluation_id>", methods=["DELETE"])
def delete_evaluation(evaluation_id):
    evaluation = session.query(Evaluation).get(evaluation_id)

    if evaluation:
        session.delete(evaluation)
        session.commit()

        return jsonify("OK"), 200

    return jsonify("Not Found"), 404


@app.route("/evaluations/service/<service_id>")
def get_service_evaluations(service_id):
    evaluations = session.query(Evaluation).filter(Evaluation.service_id == service_id)

    myList = []
    for evaluation in evaluations:
        myList.append(evaluation.as_dict())

    return jsonify(myList)


@app.route("/evaluation/create", methods=["POST"])
def create_evaluation():
    if request.is_json and request.data:
        info = {"service_id": None, "rating": None, "description": None}

        for key in request.json:  # type: ignore
            if key in info:
                info[key] = request.json[key]  # type: ignore
            else:
                return jsonify("Bad Request"), 400

        if None in info.values():
            return jsonify("Bad Request"), 400

        if info["rating"] < 1 or info["rating"] > 5:  # type: ignore
            return jsonify("Bad request"), 400

        evaluation = Evaluation(
            service_id=info["service_id"], rating=info["rating"], description=info["description"], datetime=datetime.now()
        )
        session.add(evaluation)
        session.commit()

        return jsonify("Created"), 201

    return jsonify("Bad Request"), 400


################################
############ MAIN ##############


if __name__ == "__main__":
    app.run(host=configs["host"], port=configs["port"], debug=True)
