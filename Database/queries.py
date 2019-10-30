from Database.models import ZipCode, ZipDistance
from Database import session


def get_zip_code_row(zip_string):
    return session.query(ZipCode).filter(ZipCode.zip_string == zip_string).first()


def get_zip_distance_row(zip_row_1=None, zip_row_2=None,
                         zip_id_1=None, zip_id_2=None,
                         zip_string_1=None, zip_string_2=None):

    if zip_row_1 is None:
        if zip_id_1 is None:
            if zip_string_1 is None:
                return None
            else:
                zip_row_1 = session.query(ZipCode).filter(ZipCode.zip_string == zip_string_1).first()
                if zip_row_1 is None:
                    return None
        else:
            zip_row_1 = session.query(ZipCode).filter(ZipCode.id == zip_id_1).first()
            if zip_row_1 is None:
                return None

    if zip_row_2 is None:
        if zip_id_2 is None:
            if zip_string_2 is None:
                return None
            else:
                zip_row_2 = session.query(ZipCode).filter(ZipCode.zip_string == zip_string_2).first()
                if zip_row_2 is None:
                    return None
        else:
            zip_row_2 = session.query(ZipCode).filter(ZipCode.id == zip_id_2).first()
            if zip_row_2 is None:
                return None

    return session.query(ZipDistance).filter(ZipDistance.zip_id_1 == zip_row_1.id) \
                                     .filter(ZipDistance.zip_id_2 == zip_row_2.id).first()
