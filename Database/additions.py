from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Database import ZipCode, ZipDistance, Base, DB_URL

engine = create_engine(DB_URL, echo=False)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

# session.commit() will push all staged changes to the global database
# session.rollback() will revert all staged changes
session = DBSession()


def add_zip_code(zip_string, lat, lng):
    zip_code_row = ZipCode(zip_string=zip_string, lat=lat, lng=lng)
    session.add(zip_code_row)
    session.commit()


def add_zip_distance(zip_id_1, zip_id_2, distance):
    zip_distance_row = ZipDistance(zip_id_1=zip_id_1, zip_id_2=zip_id_2, distance=distance)
    session.add(zip_distance_row)
    session.commit()


