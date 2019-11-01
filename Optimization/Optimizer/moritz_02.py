from Optimization.Optimizer import Optimizer
from Optimization.attendee import Host, Guest

import Database.queries as db_query
import Database.additions as db_addition

class HostHub:

    instances = []
    hosts = []
    guests = []

    def __init__(self):
        self.hosts = []
        self.guests = []

        self.max_guests = 0

        self.avg_lat = 0
        self.avg_lng = 0
        HostHub.instances.append(self)

    def append_hosts(self, appendix):
        if isinstance(appendix, Host):
            self.hosts.append(appendix)
            HostHub.hosts.append(appendix)
        elif isinstance(appendix, list):
            self.hosts += appendix
            HostHub.hosts += appendix

        self.update_hub()

    def append_guests(self, appendix):
        if isinstance(appendix, Guest):
            self.guests.append(appendix)
            HostHub.guests.append(appendix)
        elif isinstance(appendix, list):
            self.guests += appendix
            HostHub.guests += appendix

    def update_hub(self):
        self.max_guests = 0
        avg_lat = 0
        avg_lng = 0

        for host in self.hosts:
            self.max_guests += host.max_guests
            avg_lat += host.lat
            avg_lng += host.lng

        self.avg_lat = avg_lat/len(self.hosts)
        self.avg_lng = avg_lng/len(self.hosts)

    def export_hub(self):
        while len(self.hosts) != 0:
            host = self.hosts.pop()
            HostHub.hosts.remove(host)
            number_of_guests = round((host.max_guests/float(self.max_guests)) * len(self.guests))
            for i in range(number_of_guests):
                guest = self.guests.pop()
                host.append_guest(guest)
                HostHub.guests.remove(guest)
            self.max_guests -= host.max_guests
            # We don't need to update avg_lat/avg_lng because we
            # won't use it anymore after exporting the hub
        HostHub.instances.remove(self)


class OptimizerMoritz01(Optimizer):

    @staticmethod
    def optimize():
        print(len(Guest.instances), len(Host.instances))

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

