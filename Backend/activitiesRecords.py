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


def listServices():
    return session.query(Activities).all()

def newActivities(name,activityType , time, description, year, month,day):
   
    auth = Activities(name = name, activityType=activityType, time =time, description=description, startTime=datetime.date(year,month,day))
    session.add(auth)
    session.commit()

if __name__ == "__main__":

    if not db_exists:
        newActivities("ADINT","Class" ,"2022", "Aprender aplicações",2022, 10,6 )
      
    #queries
    print("\nAll Services")

    mylist = listServices()
    for a in mylist:
        print(a.as_dict())
    
    print(listServices())


    #for u in session.query(Presencial_Services).all():
    #    print( u.__dict__ )