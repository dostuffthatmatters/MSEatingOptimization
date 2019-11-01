from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Database import ZipCode, ZipDistance, Coordinates, CoordinatesZipDistance, Base, DB_URL

engine = create_engine(DB_URL, echo=False)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

# session.commit() will push all staged changes to the global database
# session.rollback() will revert all staged changes
session = DBSession()


def get_all_zip_code_rows():
    return session.query(ZipCode).all()


def get_zip_code_row(zip_string):
    return session.query(ZipCode).filter(ZipCode.zip_string == zip_string).first()


def get_all_zip_distance_rows():
    return session.query(ZipDistance).all()


def get_zip_distance_row(zip_string_1=None, zip_string_2=None):
    zip_row_1 = session.query(ZipCode).filter(ZipCode.zip_string == zip_string_1).first()
    zip_row_2 = session.query(ZipCode).filter(ZipCode.zip_string == zip_string_2).first()

    if zip_row_1 is None or zip_row_2 is None:
        return None

    query_12 = session.query(ZipDistance).filter(ZipDistance.zip_id_1 == zip_row_1.id) \
        .filter(ZipDistance.zip_id_2 == zip_row_2.id).first()

    query_21 = session.query(ZipDistance).filter(ZipDistance.zip_id_1 == zip_row_2.id) \
        .filter(ZipDistance.zip_id_2 == zip_row_1.id).first()

    if query_12 is None:
        return query_21
    else:
        return query_12


def get_zip_distance(zip_string_1=None, zip_string_2=None):

    zip_distance_row = get_zip_distance_row(zip_string_1=zip_string_1, zip_string_2=zip_string_2)

    if zip_distance_row is None:
        return 0.0
    else:
        return zip_distance_row.distance


def get_coordinates_zip_distance_row(zip_string=None, lat=0, lng=0):
    zip_row = session.query(ZipCode).filter(ZipCode.zip_string == zip_string).first()
    coordinates_row = session.query(Coordinates).filter(Coordinates.lat == lat).filter(Coordinates.lng == lng).first()

    if zip_row is None or coordinates_row is None:
        return None

    return session.query(CoordinatesZipDistance).filter(CoordinatesZipDistance.zip_id == zip_row.id) \
        .filter(CoordinatesZipDistance.coordinates_id == coordinates_row.id).first()


def get_coordinates_zip_distance(zip_string=None, lat=0, lng=0):

    coordinates_zip_distance_row = get_coordinates_zip_distance_row(zip_string=zip_string, lat=lat, lng=lng)

    if coordinates_zip_distance_row is None:
        return 0.0
    else:
        return coordinates_zip_distance_row.distance
