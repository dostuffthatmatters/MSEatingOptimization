from Database.models import ZipCode, ZipDistance
from Database import session


def add_zip_code(zip_string, lat, lng):
    zip_code_row = ZipCode(zip_string=zip_string, lat=lat, lng=lng)
    session.add(zip_code_row)
    session.commit()


def add_zip_distance(zip_id_1, zip_id_2, distance):
    zip_distance_row = ZipDistance(zip_id_1=zip_id_1, zip_id_2=zip_id_2, distance=distance)
    session.add(zip_distance_row)
    session.commit()


