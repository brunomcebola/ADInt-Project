from email import message
from fileinput import filename
from multiprocessing import context
from unicodedata import name
from flask import Flask, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename

import requests
import json

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date

from sqlalchemy import inspect

import json
import datetime
from sqlalchemy.orm import sessionmaker
from os import path


#SLQ access layer initialization
DATABASE_FILE = "./Databases/CoursesDB.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t WARNING: DATABASE ALREADY EXISTS ")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

#Declaration of data
class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True) 
    name = Column(String) # Name of the Course. Example: Aplicações Distribuidas da Internet
    professor = Column(Integer) # Professor. Example: Jnos
    year = Column(String) # Year. Example: 2022/2023
    description = Column(String) # Desciption. Example: Learning REST API
    
    
    def __repr__(self):
        return "<Course(id=%d name='%s', professor='%s', year='%s', description='%s')>" % (
                                self.id, self.name, self.professor, self.year, self.description)
    def as_dict(self):
        return {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }
    



Base.metadata.create_all(engine) #Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()


def listCourses():
    return session.query(Course).all()

def newCourse(name,professor , year, description):
    auth = Course(name = name, professor=professor, year =year, description=description)
    session.add(auth)
    session.commit()

if __name__ == "__main__":

    if not db_exists:
        newCourse("ADINT","Jnos" ,"2022/2023", "Aprender aplicações" )
        newCourse("CINT","Nuno Horta" ,"2022/2023", "Computação Inteligente" )
        newCourse("PIC","Pedro Lima" ,"2022/2023", "Preparação da Tese" )

################################
########### FLASK ##############

app = Flask(__name__)

@app.route('/createCourse', methods=['GET', 'POST'])
def createCourse():
    if request.method == 'POST':
        if "Token" in request.headers:
            if request.headers['Token'] == "proxy":
                name=""
                professor=""
                year = ""
                description=""
                result = request.json
                print(result)
                for key, value in result.items():
                    if key == 'name':
                        name = value
                    if key == 'professor':
                        professor = value
                    if key == 'description':
                        description = value
                    if key == 'year':
                        year = value
                    
                if name == "" and description == "" and year == "" and professor=="":
                    return "You didn't put anything", 400
                
                #create Service
                newCourse(name=name,professor=professor , year=year, description=description)

                return result , 200
            return "Permission Denied", 401
        return "Header Invalid", 400

@app.route('/listCourses')
def getAllCourses():
    if "Token" in request.headers:
        if request.headers['Token'] == "proxy":
            myList = []

            courses = listCourses()

            for course in courses:
                myList.append(course.as_dict())

            return myList, 200
        return "Permission Denied", 401
    return "Header Invalid", 400


################################
############ MAIN ##############


if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=8001, debug=True)
