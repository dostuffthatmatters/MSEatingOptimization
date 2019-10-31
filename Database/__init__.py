from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float


DB_URL = 'sqlite:///database.db'

Base = declarative_base()

class ZipCode(Base):
    __tablename__ = 'zip_code'
    id = Column(Integer, primary_key=True)

    zip_string = Column(String)

    lat = Column(Float)
    lng = Column(Float)

    def __repr__(self):
        return f"<ZipCode(zip: '{self.zip_string}', coordinates: {self.lat}N, {self.lng}E)>"


class ZipDistance(Base):
    __tablename__ = 'zip_distance'
    id = Column(Integer, primary_key=True)

    zip_id_1 = Column(Integer)
    zip_id_2 = Column(Integer)

    distance = Column(Float)

    def __repr__(self):
        return f"<ZipDistance(zip_id_1: {self.zip_id_1}, zip_id_1: {self.zip_id_1}, distance: {self.distance})>"


engine = create_engine(DB_URL, echo=False)
# engine = create_engine('sqlite:///:memory:', echo=True)

# Create all tables in the engine.
Base.metadata.create_all(engine)
