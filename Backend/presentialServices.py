from email import message
from fileinput import filename
from multiprocessing import context
from operator import methodcaller
from flask import Flask, request, send_from_directory, redirect, url_for, render_template
from werkzeug.utils import secure_filename

import requests
import json

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

from sqlalchemy import inspect

from sqlalchemy.orm import sessionmaker
from os import path


#SLQ access layer initialization
DATABASE_FILE = "./Databases/PresentialServicesDB.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t WARNING: DATABASE ALREADY EXISTS ")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), 
                        connect_args={'check_same_thread': False},
                        echo=False) #echo = True shows all SQL calls

Base = declarative_base()

#Declaration of data
class Presencial_Services(Base):
    __tablename__ = 'presencial_services'
    id = Column(Integer, primary_key=True) 
    title = Column(String) # Title of the Serice. Example: Bar de Civil
    description = Column(String) # Desciption. Example: Sells food and drinks
    location = Column(String) # Location of the Serice. Example: Civil's Building
    
    def __repr__(self):
        return "<Presencial_Services(id=%d title='%s', description='%s', location=%s)>" % (
                                self.id, self.title, self.description, self.location)
    def as_dict(self):
        return {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }

Base.metadata.create_all(engine) #Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()


def listServices():
    return session.query(Presencial_Services).all()

def newService(title , description, location):
    auth = Presencial_Services(title = title, description=description, location=location)
    session.add(auth)
    session.commit()
    


if not db_exists:
    newService("Cantina" , "Vende Comida","Torre de Eletro")
    newService("Campo" , "Praticar Futsal","Ao pé da secção de folhas")
    newService("Secretaria" ,"Papelada","Edificio Central")
        
#queries

"""
print("\nAll Services")

mylist = listServices()
for a in mylist:
    print(a.as_dict())
"""

################################
########### FLASK ##############

app = Flask(__name__)

@app.route('/createService', methods=['GET', 'POST'])
def createService():
    if request.method == 'POST':
        title=""
        description=""
        location = ""
        result = request.json
        print(result)
        for key, value in result.items():
            if key == 'title':
                title = value
            if key == 'description':
                description = value
            if key == 'location':
                location = value
            
        if title == "" and description == "" and location == "":
            return "You didn't put anything", 400
        
        #create Service
        newService(title=title,description=description, location=location)

        return result, 200

@app.route('/listServices')
def getAllServices():
    myList = []

    services = listServices()

    for service in services:
        myList.append(service.as_dict())
    print(json.dumps(myList))
    return json.dumps(myList)


################################
############ MAIN ##############


if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=8000, debug=True)
