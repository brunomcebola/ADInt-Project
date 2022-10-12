from sqlalchemy.orm import sessionmaker
from flask import Flask, request, jsonify
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String

from aux_functions import *

# read and validate configurations
config_file = "./config/presentialServices.yaml"

configs = read_yaml(config_file)

validate_yaml(configs, ["db_path", "db_name", "host", "port"], config_file)


# create DB and table
Base = declarative_base()


class Presencial_Service(Base):
    __tablename__ = "presencial_services"
    id = Column(Integer, primary_key=True)
    name = Column(String)  # Name of the Service. Example: Bar de Civil
    description = Column(String)  # Desciption. Example: Sells food and drinks
    location = Column(String)  # Location of the Serice. Example: Civil's Building

    def __repr__(self):
        return "<Presencial_Service(id=%d name='%s', description='%s', location=%s)>" % (
            self.id,
            self.name,
            self.description,
            self.location,
        )

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


@app.route("/services")
def get_services():
    services = session.query(Presencial_Service).all()

    myList = []
    for service in services:
        myList.append(service.as_dict())

    return jsonify(myList)


@app.route("/service/<id>", methods=["GET", "DELETE"])
def get_and_delete_service(id):
    if request.method == "GET":
        service = session.query(Presencial_Service).get(id)

        if service:
            return jsonify(service.as_dict())

        return jsonify("Not Found"), 404

    else:
        service = session.query(Presencial_Service).get(id)
        session.delete(service)
        session.commit()

        return jsonify("OK"), 200


@app.route("/service/create", methods=["POST"])
def create_service():

    if request.is_json and request.data:
        info = {"name": None, "description": None, "location": None}

        for key in request.json:  # type: ignore
            if key in info:
                info[key] = request.json[key]  # type: ignore
            else:
                return jsonify("Bad Request"), 400

        if None in info.values():
            return jsonify("Bad Request"), 400

        service = Presencial_Service(name=info["name"], description=info["description"], location=info["location"])
        session.add(service)
        session.commit()

        return jsonify("Created"), 201

    return jsonify("Bad Request"), 400


################################
############ MAIN ##############


if __name__ == "__main__":
    app.run(host=configs["host"], port=configs["port"], debug=True)
