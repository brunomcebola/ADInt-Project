from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date

from sqlalchemy import inspect

import json
import datetime
from sqlalchemy.orm import sessionmaker
from os import path


#SLQ access layer initialization
DATABASE_FILE = "presentialServicesDB.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t WARNING: DATABASE ALREADY EXISTS ")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

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


def getAuthor(serviceID):
    return session.query(Presencial_Services).filter(Presencial_Services.id==serviceID).first()

def newService(title , description, location):
    auth = Presencial_Services(title = title, description=description, location=location)
    session.add(auth)
    session.commit()

if __name__ == "__main__":

    if not db_exists:
        newService("Cantina" , "Vende Comida","Torre de Eletro")
        newService("Campo" , "Praticar Futsal","Ao pé da secção de folhas")
        newService("Secretaria" ,"Papelada","Edificio Central")
      
    #queries
    print("\nAll Services")

    mylist = listServices()
    for a in mylist:
        print(a.as_dict())
    
    print(listServices())


    #for u in session.query(Presencial_Services).all():
    #    print( u.__dict__ )