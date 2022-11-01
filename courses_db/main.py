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


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    professor = Column(String)
    school_year = Column(String)
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


################################
########### FLASK ##############

app = Flask(__name__)


@app.before_request
def before_request():
    return check_auth_token()


@app.route("/courses")
def get_courses():
    courses = session.query(Course).all()

    my_list = []
    for course in courses:
        my_list.append(course.as_dict())

    return jsonify(my_list), 200


@app.route("/courses/filter")
def get_filtered_courses():
    filters = request.args.to_dict()
    allowed_filters = Course.columns()

    for filter_key in filters:
        if filter_key not in allowed_filters:
            return jsonify("Bad Request"), 400

    courses = session.query(Course)
    for attr, value in filters.items():
        courses = courses.filter(getattr(Course, attr).like("%%%s%%" % value))

    my_list = []
    for course in courses:
        my_list.append(course.as_dict())

    return jsonify(my_list), 200


@app.route("/course/<course_id>")
def get_course(course_id):
    course = session.query(Course).get(course_id)

    if course:
        return jsonify(course.as_dict()), 200

    return jsonify("Not Found"), 404


@app.route("/course/<course_id>", methods=["DELETE"])
def delete_course(course_id):
    course = session.query(Course).get(course_id)

    if course:
        session.delete(course)
        session.commit()

        return jsonify("OK"), 200

    return jsonify("Not Found"), 404


@app.route("/course/create", methods=["POST"])
def create_course():
    if request.is_json and request.data:
        data = {}
        allowed_fields = Course.columns()
        allowed_fields.remove("id")
        mandatory_fileds = ["name", "professor", "school_year"]

        for key in request.json:  # type: ignore
            if key in allowed_fields:
                data[key] = request.json[key]  # type: ignore
            else:
                return jsonify("Bad Request"), 400

        for field in mandatory_fileds:
            if field not in data:
                return jsonify("Bad Request"), 400

        course = Course()

        for key, value in data.items():
            setattr(course, key, value)

        session.add(course)
        session.commit()

        return jsonify("Created"), 201

    return jsonify("Bad Request"), 400


################################
############ MAIN ##############

if __name__ == "__main__":
    app.run(host=os.getenv("HOST"), port=int(str(os.getenv("PORT"))), debug=True)
