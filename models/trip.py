from sqlalchemy import Sequence, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator
from geoalchemy2.types import Geometry

Base = declarative_base()

class Point(TypeDecorator):
    impl = Geometry('POINT')

class Trip(Base):
    __tablename__ = 'trips'

    id = Column(Integer, Sequence('trip_id_seq'), primary_key=True)
    region = Column(String)
    origin_coord = Column(Point)
    destination_coord = Column(Point)
    datetime = Column(DateTime)
    datasource = Column(String)
