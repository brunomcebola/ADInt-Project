import os

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from middlewares import *


mandatory_params = [
    "HOST",
    "PORT",
    "DB_NAME",
]

load_dotenv()

for param in mandatory_params:
    if not os.getenv(param):
        raise SystemExit("[ENV] Parameter %s is mandatory" % param)

# create DB and table
Base = declarative_base()


class PresencialService(Base):
    __tablename__ = "presencial_services"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(String)
    description = Column(String, default="")

    @classmethod
    def columns(cls):
        return [column.key for column in cls.__table__.columns]

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


DATABASE_FILE = str(os.getenv("DB_NAME")).strip() + ".sqlite"

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


@app.route("/services")
def get_services():
    services = session.query(PresencialService).all()

    myList = []
    for service in services:
        myList.append(service.as_dict())

    return jsonify(myList), 200


@app.route("/services/filter")
def get_filtered_services():
    filters = request.args.to_dict()
    allowed_filters = PresencialService.columns()

    for filter_key in filters:
        if filter_key not in allowed_filters:
            return jsonify("Bad Request"), 400

    services = session.query(PresencialService)
    for attr, value in filters.items():
        services = services.filter(getattr(PresencialService, attr).like("%%%s%%" % value))

    my_list = []
    for service in services:
        my_list.append(service.as_dict())

    return jsonify(my_list), 200


@app.route("/service/<service_id>")
def get_service(service_id):
    service = session.query(PresencialService).get(service_id)

    if service:
        return jsonify(service.as_dict()), 200

    return jsonify("Not Found"), 404


@app.route("/service/<service_id>", methods=["DELETE"])
def delete_service(service_id):
    service = session.query(PresencialService).get(service_id)

    if service:
        session.delete(service)
        session.commit()

        return jsonify("OK"), 200

    return jsonify("Not Found"), 404


@app.route("/service/create", methods=["POST"])
def create_service():
    if request.is_json and request.data:
        data = {}
        allowed_fields = PresencialService.columns()
        allowed_fields.remove("id")
        mandatory_fileds = ["name", "location"]

        for key in request.json:  # type: ignore
            if key in allowed_fields:
                data[key] = request.json[key]  # type: ignore
            else:
                return jsonify("Bad Request"), 400

        for field in mandatory_fileds:
            if field not in data:
                return jsonify("Bad Request"), 400

        service = PresencialService()

        for key, value in data.items():
            setattr(service, key, value)

        session.add(service)
        session.commit()

        return jsonify("Created"), 201

    return jsonify("Bad Request"), 400


################################
############ MAIN ##############


if __name__ == "__main__":
    app.run(host=os.getenv("HOST"), port=int(str(os.getenv("PORT"))), debug=True)
