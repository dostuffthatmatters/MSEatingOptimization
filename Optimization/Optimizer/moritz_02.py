
from Optimization.Optimizer import Optimizer
from Optimization.attendee import Host, Guest

from Helpers.custom_printing import CustomPrinting

import Database.queries as db_query

class HostHub:

    MAX_DISTANCE_BETWEEN_HOSTS = 500

    instances = []
    hosts = []
    guests = []

    @staticmethod
    def create_hubs():
        for host in Host.instances:
            added_to_hub = False
            for host_hub in HostHub.instances:
                for zip_string in host_hub.zip_strings:
                    if host.zip_string == zip_string:
                        host_hub.append_host(host)
                        added_to_hub = True
                        break
                    elif db_query.get_zip_distance(zip_string_1=host.zip_string, zip_string_2=zip_string) < HostHub.MAX_DISTANCE_BETWEEN_HOSTS:
                        host_hub.append_host(host)
                        added_to_hub = True
                        break
                if added_to_hub:
                    CustomPrinting.print_yellow(f"Extended HostHub at {host_hub.avg_lat}, {host_hub.avg_lng} -> {host_hub.zip_strings}")
                    break

            if not added_to_hub:
                new_host_hub = HostHub()
                new_host_hub.append_hosts(host)
                CustomPrinting.print_yellow(f"New HostHub at: {new_host_hub.avg_lat}, {new_host_hub.avg_lng} -> {new_host_hub.zip_strings}")


    def __init__(self):
        self.hosts = []
        self.guests = []

        self.max_guests = 0

        self.avg_lat = 0
        self.avg_lng = 0
        self.zip_strings = []
        HostHub.instances.append(self)

    def append_hosts(self, appendix):
        if isinstance(appendix, Host):
            self.hosts.append(appendix)
            HostHub.hosts.append(appendix)
            self.zip_strings.append(appendix.zip_string)
        elif isinstance(appendix, list):
            self.hosts += appendix
            HostHub.hosts += appendix
            for host in appendix:
                self.zip_strings.append(host.zip_string)

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

        # Sort guests by distance to the center of the hub so that
        # the closest guests are assigned first
        for guest in self.guests:
            distance = 0
            for zip_string in self.zip_strings:
                distance += db_query.get_zip_distance(zip_string_1=guest.zip_string, zip_string_2=zip_string)
            distance /= float(len(self.zip_strings))
            guest.distance_to_hub = distance

        self.guests = sorted(self.guests, key=lambda x: x.distance_to_hub)

        # Looping through hosts in a circle increasing each host
        # that is not full yet by one guest
        host_index = 0
        guest_index = 0

        # Iterating through all guests assigned to this hub
        while guest_index < len(self.guests):
            guest = self.guests[guest_index]
            host = self.hosts[host_index]

            # Kicking a host out of this hub when he is filled up
            if len(host.guests) >= host.max_guests:
                self.hosts.remove(host)

                # HostHubs are no longer keeping track of that host
                HostHub.hosts.remove(host)
            else:
                host.append_guest(guest)
                host_index += 1
                guest_index += 1

                # HostHubs are no longer keeping track of that guest
                HostHub.guests.remove(guest)

            if len(self.hosts) == 0:
                # If there are no hosts left to assign guests to
                break
            else:
                host_index = host_index % len(self.hosts)

        # After
        for host in self.hosts:
            HostHub.hosts.remove(host)


class OptimizerMoritz02(Optimizer):

    @staticmethod
    def optimize():
        CustomPrinting.print_pink(f"Optimizing: {len(Guest.instances)} guests and {len(Host.instances)} hosts.")

        HostHub.create_hubs()

        for guest in Guest.instances:
            favorite_host_hub = None
            favorite_distance = 0
            for host_hub in HostHub.instances:
                distance = 0
                for zip_string in host_hub.zip_strings:
                    distance += db_query.get_zip_distance(zip_string_1=guest.zip_string, zip_string_2=zip_string)

                distance /= float(len(host_hub.zip_strings))

                if favorite_host_hub is None:
                    favorite_host_hub = host_hub
                    favorite_distance = distance
                elif favorite_distance > distance:
                    favorite_host_hub = host_hub
                    favorite_distance = distance

            favorite_host_hub.append_guests(guest)

        for host_hub in HostHub.instances:
            CustomPrinting.print_yellow(f"Host hub {host_hub.zip_strings}: {len(host_hub.guests)} guests and {len(host_hub.hosts)} hosts")
            host_hub.export_hub()


