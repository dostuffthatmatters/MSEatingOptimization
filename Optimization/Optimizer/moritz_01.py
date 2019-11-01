from Optimization.Optimizer import Optimizer
from Optimization.attendee import Host, Guest

import Database.queries as db_query
import Database.additions as db_addition

class OptimizerMoritz01(Optimizer):

    @staticmethod
    def optimize():
        for guest in Guest.instances:
            favorite_host = None
            favorite_distance = 0
            for host in Host.instances:
                if guest.zip_string == host.zip_string:
                    distance = 0
                else:
                    distance = db_query.get_zip_distance_row(zip_string_1=guest.zip_string, zip_string_2=host.zip_string).distance

                if favorite_host is None:
                    favorite_host = host
                    favorite_distance = distance
                elif favorite_distance > distance:
                    favorite_host = host
                    favorite_distance = distance
            guest.host = favorite_host
            favorite_host.guests.append(guest)

