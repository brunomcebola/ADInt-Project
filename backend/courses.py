from os.path import exists
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, jsonify
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine

from auxFunctions import *

# read and validate configurations
config_file = "./config/courses.yaml"

configs = read_yaml(config_file)

validate_yaml(configs, ["db_path", "db_name", "host", "port"], config_file)

# create DB and table
Base = declarative_base()


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    name = Column(String)  # Name of the Course. Example: Aplicações Distribuidas da Internet
    professor = Column(String)  # Professor. Example: Jnos
    school_year = Column(String)  # Year. Example: 2022/2023
    description = Column(String)  # Desciption. Example: Learning REST API

    def __repr__(self):
        return "<Course(id=%d name='%s', professor='%s', school_year='%s', description='%s')>" % (
            self.id,
            self.name,
            self.professor,
            self.school_year,
            self.description,
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


@app.route("/courses")
def get_courses():
    courses = session.query(Course).all()

    myList = []
    for course in courses:
        myList.append(course.as_dict())

    return jsonify(myList)


@app.route("/course/<id>", methods=["GET", "DELETE"])
def get_and_delete_course(id):
    if request.method == "GET":
        course = session.query(Course).get(id)

        if course:
            return jsonify(course.as_dict())

        return jsonify("Not Found"), 404

    else:
        course = session.query(Course).get(id)
        session.delete(course)
        session.commit()

        return jsonify("OK"), 200


@app.route("/course/create", methods=["POST"])
def create_course():

    if request.is_json and request.data:
        info = {"name": None, "professor": None, "school_year": None, "description": None}

        for key in request.json:  # type: ignore
            if key in info:
                info[key] = request.json[key]  # type: ignore
            else:
                return jsonify("Bad Request"), 400

        if None in info.values():
            return jsonify("Bad Request"), 400

        course = Course(
            name=info["name"], professor=info["professor"], school_year=info["school_year"], description=info["description"]
        )
        session.add(course)
        session.commit()

        return jsonify("Created"), 201

    return jsonify("Bad Request"), 400


################################
############ MAIN ##############

if __name__ == "__main__":
    app.run(host=configs["host"], port=configs["port"], debug=True)
