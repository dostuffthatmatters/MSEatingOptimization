import csv
from Optimization.attendee import Host, Guest
from Helpers.custom_math import CustomMath
from Helpers.custom_printing import CustomPrinting

import Database.queries as db_query
import Database.additions as db_addition


class Optimization:

    def __init__(self, input_file="Source/in.csv", output_file="Source/out.csv"):
        self.input_file = input_file
        self.output_file = output_file

        self.load_models()
        Optimization.update_distances()

    def load_models(self):
        with open(self.input_file, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in spamreader:

                # Skip first row
                if row[0] == 'Region':
                    continue

                kwargs = {
                    "region": row[0],
                    "allergies": row[2],
                    "max_people": row[3],
                    "street_and_number": row[6],
                    "zip_code_and_city": row[7],
                    "name": row[4] + " " + row[5],
                    "mail": row[8],
                    "phone_number": row[9],
                    "semester": row[10]
                }

                if row[1] == 'Ja':
                    # Pass parameters
                    Host(True, **kwargs)
                else:
                    # Pass parameters
                    Guest(False, **kwargs)

    @staticmethod
    def update_distances():
        zip_code_rows = db_query.get_all_zip_code_rows()
        desired_length = 0
        for i in range(len(zip_code_rows)):
            desired_length += i

        actual_length = len(db_query.get_all_zip_distance_rows())
        CustomPrinting.print_yellow(f"{actual_length}/{desired_length} distances already calculated")

        if desired_length != actual_length:

            for zip_code_row_1 in zip_code_rows:
                for zip_code_row_2 in zip_code_rows:
                    if zip_code_row_1.id == zip_code_row_2.id:
                        continue
                    distance_query = db_query.get_zip_distance_row(zip_id_1=zip_code_row_1.id, zip_id_2=zip_code_row_2.id)
                    if distance_query is None:
                        CustomPrinting.print_yellow(f"Now calculating distance between {zip_code_row_1.zip_string} "
                                                    f"and {zip_code_row_2.zip_string})")
                        origin = (zip_code_row_1.lat, zip_code_row_1.lng)
                        destination = (zip_code_row_1.lat, zip_code_row_1.lng)
                        distance = CustomMath.haversine(origin, destination)
                        db_addition.add_zip_distance(zip_code_row_1.id, zip_code_row_2.id, distance)
        else:
            CustomPrinting.print_yellow(f"No distances left to be calculated")


    @staticmethod
    def execute():
        return True, ""
