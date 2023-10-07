from sqlalchemy import Sequence, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Trip(Base):
    __tablename__ = 'trips'

    id = Column(Integer, Sequence('trip_id_seq'), primary_key=True)
    region = Column(String)
    origin_x = Column(Float)
    origin_y = Column(Float)
    destination_x = Column(Float)
    destination_y = Column(Float)
    datetime = Column(DateTime)
    datasource = Column(String)
