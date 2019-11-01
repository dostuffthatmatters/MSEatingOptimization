from Optimization import csv_link
from Optimization import visual_link

from Optimization.attendee import Host, Guest
from Helpers.custom_math import CustomMath
from Helpers.custom_printing import CustomPrinting

import Database.queries as db_query
import Database.additions as db_addition

from Optimization.Optimizer.moritz_01 import OptimizerMoritz01
from Optimization.Optimizer.moritz_02 import OptimizerMoritz02
from Optimization.Optimizer.moritz_03 import OptimizerMoritz03

from time import time


class Optimization:

    def __init__(self, input_file="Source/in.csv", output_file="Source/out.csv", optimizer=OptimizerMoritz03):
        self.input_file = input_file
        self.output_file = output_file

        csv_link.load_models(self.input_file)
        Optimization.update_distances()
        self.optimizer = optimizer

    @staticmethod
    def update_distances():

        zip_code_rows = db_query.get_all_zip_code_rows()
        desired_length = 0
        for i in range(len(zip_code_rows)):
            desired_length += i

        CustomPrinting.print_pink(f"#2 Updating Distances ...")
        time1 = time()

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
                        destination = (zip_code_row_2.lat, zip_code_row_2.lng)
                        distance = CustomMath.haversine(origin, destination)
                        CustomPrinting.print_yellow(f"origin={origin}, destination={destination}")
                        CustomPrinting.print_yellow(f"Distance={distance}")
                        db_addition.add_zip_distance(zip_code_row_1.id, zip_code_row_2.id, distance)
        else:
            CustomPrinting.print_yellow(f"No distances left to be calculated")

        timespan = round(time() - time1, 6)
        CustomPrinting.print_pink(f"#2 Updating Distances: Done ({timespan} seconds).", new_lines=3)

    def execute(self):
        self.optimizer.optimize()
        csv_link.export_models(self.output_file)
        visual_link.export_image()
        return True, ""
