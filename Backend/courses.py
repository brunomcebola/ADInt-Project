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


def listServices():
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
      
    #queries
    print("\nAll Services")

    mylist = listServices()
    for a in mylist:
        print(a.as_dict())
    
    print(listServices())


    #for u in session.query(Presencial_Services).all():
    #    print( u.__dict__ )