from calendar import month
from email import message
from fileinput import filename
from multiprocessing import context
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
DATABASE_FILE = "./Databases/ActivitiesDB.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t WARNING: DATABASE ALREADY EXISTS ")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

#Declaration of data
class Activities(Base):
    __tablename__ = 'activities'
    id = Column(Integer, primary_key=True) 
    name = Column(String) # Name of the Activity. Example: Aplicações Distribuidas da Internet
    activityType = Column(String) # Activity Type. Example: Aula/Serviço
    time = Column(Integer) # Professor. Example: 2 hours
    description = Column(String) # Desciption. Example: Learning REST API
    startTime = Column(Date) # Year. Example: 3-2-2022
    
    
    def __repr__(self):
        return "<Activities(id=%d name='%s', activityType='%s', time='%s', description='%s', startTime='%s')>" % (
                                self.id, self.name, self.activityType, self.time, self.description, str(self.startTime))
    def as_dict(self):
        return {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }
    



Base.metadata.create_all(engine) #Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()


def listActivities():
    return session.query(Activities).all()

def newActivities(name,activityType , time, description, year, month,day):
   
    auth = Activities(name = name, activityType=activityType, time =time, description=description, startTime=datetime.date(year,month,day))
    session.add(auth)
    session.commit()

if __name__ == "__main__":

    if not db_exists:
        newActivities("ADINT","Class" ,"2 hours", "Aprender aplicações",2022, 10,6 )

################################
########### FLASK ##############

app = Flask(__name__)

@app.route('/createActivity/request', methods=['GET', 'POST'])
def createCourse():
    if request.method == 'POST':
        name=""
        activityType=""
        year = ""
        time=""
        month=""
        day=""
        description=""
        result = request.form
        print(result)
        for key, value in result.items():
            if key == 'name':
                name = value
            if key == 'activityType':
                activityType = value
            if key == 'year':
                year = value
            if key == 'time':
                time = value
            if key == 'month':
                month = value
            if key == 'day':
                day = value
            if key =="description":
                description=value
            
        if name == "" and year == "" and activityType=="" and time =="" and day=="" and month=="":
            return "You didn't put anything", 400
        
        #create Service
        newActivities(name=name,activityType=activityType , 
                    time=time, description=description, year=year, month=month,day=day)

        return "Resultou" , 200

@app.route('/listActivities')
def getAllCourses():
    myList = []

    activities = listActivities()

    for activity in activities:
        myList.append(activity.as_dict())

    return myList


################################
############ MAIN ##############


if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=8002, debug=True)
