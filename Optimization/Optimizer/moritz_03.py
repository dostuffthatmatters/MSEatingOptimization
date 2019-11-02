from Optimization.Optimizer import Optimizer
from Optimization.attendee import Host, Guest

from Helpers.custom_logger import CustomLogger

import Database.queries as db_query

from time import time


class HostHub:
    MAX_DISTANCE_BETWEEN_HOSTS = 500

    instances = []

    @staticmethod
    def create_hubs():
        for host in Host.instances:
            added_to_hub = False
            for host_hub in HostHub.instances:
                for zip_string in host_hub.zip_strings:
                    if host.zip_string == zip_string:
                        host_hub.append_hosts(host)
                        added_to_hub = True
                        break
                    elif db_query.get_zip_distance(zip_string_1=host.zip_string,
                                                   zip_string_2=zip_string) < HostHub.MAX_DISTANCE_BETWEEN_HOSTS:
                        host_hub.append_hosts(host)
                        added_to_hub = True
                        break
                if added_to_hub:
                    CustomLogger.debug(f"Extended HostHub at {host_hub.zip_strings}")
                    break

            if not added_to_hub:
                new_host_hub = HostHub()
                new_host_hub.append_hosts(host)
                CustomLogger.debug(f"New HostHub at {new_host_hub.zip_strings}")

    @staticmethod
    def update_distances():
        pass

    @staticmethod
    def export_hubs():
        HostHub.instances = sorted(HostHub.instances, key=lambda x: len(x.guests) / float(x.max_guests))
        for host_hub in HostHub.instances[::-1]:
            CustomLogger.debug(f"Exporting HostHub at {host_hub.zip_strings}: {len(host_hub.guests)} guests and {len(host_hub.hosts)} hosts")
            host_hub.export_hub()

    def __init__(self):
        self.hosts = []
        self.guests = []

        self.max_guests = 0

        self.zip_strings = []
        HostHub.instances.append(self)

    def append_hosts(self, appendix):
        if isinstance(appendix, Host):
            self.hosts.append(appendix)
            self.max_guests += appendix.max_guests
            if appendix.zip_string not in self.zip_strings:
                self.zip_strings.append(appendix.zip_string)
        elif isinstance(appendix, list):
            self.hosts += appendix
            for host in appendix:
                self.max_guests += host.max_guests
                if host.zip_string not in self.zip_strings:
                    self.zip_strings.append(host.zip_string)

    def append_guests(self, appendix):
        if isinstance(appendix, Guest):
            self.guests.append(appendix)
        elif isinstance(appendix, list):
            self.guests += appendix

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
            else:
                host.append_guest(guest)
                host_index += 1
                guest_index += 1

            if len(self.hosts) == 0:
                # If there are no hosts left to assign guests to
                break
            else:
                host_index = host_index % len(self.hosts)

        # After the export this HostHub gets removed from the HostHub
        # instance-list ONLY IF this HostHub is filled up
        if len(self.hosts) == 0:
            HostHub.instances.remove(self)
            for guest in self.guests:
                # Each guest that has not been assigned to this hub
                # removes this hub from its favorite-hubs-list
                guest.switch_host_hub(HostHub.instances)

    def __repr__(self):
        return f"HostHub(Zip String: {self.zip_strings}, Hosts: {len(self.hosts)}, Guests: {len(self.guests)}, MaxGuests: {self.max_guests})"



class OptimizerMoritz03(Optimizer):

    @staticmethod
    def optimize():

        CustomLogger.info(f"#3A Creating HostHubs: {len(Host.instances)} hosts ...")
        time1 = time()
        HostHub.create_hubs()
        CustomLogger.info(f"#3A Creating HostHubs: Done ({round(time() - time1, 6)} seconds).")

        CustomLogger.info(
            f"#3B Determining each Guest's favorite HostHubs: {len(Guest.instances)} guests and {len(HostHub.instances)} host hubs ({len(Host.instances)} hosts) ...")
        time1 = time()
        OptimizerMoritz03.determine_favorite_host_hubs()
        CustomLogger.info(f"#3B Determining each Guest's favorite HostHubs: Done ({round(time() - time1, 6)} seconds).")

        CustomLogger.info(f"#3C Exporting HostHubs ...")
        time1 = time()
        HostHub.export_hubs()
        CustomLogger.info(f"#3C Exporting HostHubs: Done ({round(time() - time1, 6)} seconds).")

    @staticmethod
    def determine_favorite_host_hubs():
        for guest in Guest.instances:
            favorite_host_hubs = []
            for host_hub in HostHub.instances:
                distance = 0
                for zip_string in host_hub.zip_strings:
                    distance += db_query.get_zip_distance(zip_string_1=guest.zip_string, zip_string_2=zip_string)
                distance = round(distance/float(len(host_hub.zip_strings)), 3)
                favorite_host_hubs.append({"hub": host_hub, "distance": distance})

            favorite_host_hubs = sorted(favorite_host_hubs, key=lambda x: x["distance"])

            favorite_host_hubs[0]["hub"].append_guests(guest)
            guest.favorite_host_hubs = favorite_host_hubs

            CustomLogger.debug("Guests favorite_host_hubs",
                               data_dict={"favorite_host_hubs": [str(host) for host in guest.favorite_host_hubs]})

            if len(guest.favorite_host_hubs) != len(HostHub.instances):
                CustomLogger.warning("Guest does not have all HostHubs listed as his favorite hubs.",
                                     data_dict={"Number of HostHub.instances": len(HostHub.instances),
                                                "Number of favorite_host_hubs": len(guest.favorite_host_hubs),
                                                "favorite_host_hubs": guest.favorite_host_hubs})
