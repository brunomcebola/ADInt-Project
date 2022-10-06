from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date

from sqlalchemy import inspect

import json
import datetime
from sqlalchemy.orm import sessionmaker
from os import path


#SLQ access layer initialization
DATABASE_FILE = "./Databases/EvaluationDB.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t WARNING: DATABASE ALREADY EXISTS ")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

#Declaration of data
class Evaluation(Base):
    __tablename__ = 'evaluation'
    id = Column(Integer, primary_key=True) 
    title = Column(String) # Title of the Serice. Example: Bar de Civil
    rating = Column(Integer) # Rating. Example: 2
    
    
    def __repr__(self):
        return "<Evaluation(id=%d title='%s', rating='%s')>" % (
                                self.id, self.title, self.rating)
    def as_dict(self):
        return {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }
    



Base.metadata.create_all(engine) #Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()


def listServices():
    return session.query(Evaluation).all()

def newEvaluation(title , rating):
    auth = Evaluation(title = title, rating=rating)
    session.add(auth)
    session.commit()

if __name__ == "__main__":

    if not db_exists:
        newEvaluation("Cantina" ,3 )
        newEvaluation("Campo" , 4)
        newEvaluation("Secretaria" ,2)
      
    #queries
    print("\nAll Services")

    mylist = listServices()
    for a in mylist:
        print(a.as_dict())
    
    print(listServices())


    #for u in session.query(Presencial_Services).all():
    #    print( u.__dict__ )