from Optimization.Optimizer import Optimizer
from Optimization.attendee import Host, Guest

from Helpers.custom_logger import CustomLogger
from Helpers.custom_printing import CustomPrinting

import Database.queries as db_query

from time import time
import copy


class HostHub:
    MAX_DISTANCE_BETWEEN_HOSTS = 500

    instances = []

    def __init__(self):
        self.hosts = []

        self.guests_taken = []
        self.max_guests_left = 0
        self.favorite_guests = []

        self.zip_strings = []
        HostHub.instances.append(self)

    def filled_up(self):
        return self.max_guests_left <= 0

    def append_hosts(self, appendix):
        if isinstance(appendix, Host):
            self.hosts.append(appendix)
            self.max_guests_left += appendix.max_guests
            if appendix.zip_string not in self.zip_strings:
                self.zip_strings.append(appendix.zip_string)
        elif isinstance(appendix, list):
            self.hosts += appendix
            for host in appendix:
                self.max_guests_left += host.max_guests
                if host.zip_string not in self.zip_strings:
                    self.zip_strings.append(host.zip_string)

    def append_guests(self, appendix):
        if isinstance(appendix, Guest):
            self.guests_taken.append(appendix)
            self.max_guests_left -= 1
            appendix.assigned_to_hub = True
            for host_hub in HostHub.instances:
                host_hub.remove_guest_from_favorites(appendix)
        elif isinstance(appendix, list):
            self.guests_taken += appendix
            self.max_guests_left -= len(appendix)
            for guest in appendix:
                guest.assigned_to_hub = True
                for host_hub in HostHub.instances:
                    host_hub.remove_guest_from_favorites(guest)

        if self.max_guests_left <= 0:
            for guest in Guest.instances:
                guest.remove_host_hub_from_favorites(self)

    def remove_guest_from_favorites(self, guest):
        self.favorite_guests = list(filter(lambda x: x["guest"] != guest, self.favorite_guests))

    def initial_take(self):
        guests_which_want_this_hub = []
        for guest in Guest.instances:
            if guest.favorite_host_hubs[0]["hub"] == self:
                guests_which_want_this_hub.append(guest)

        if len(guests_which_want_this_hub) <= self.max_guests_left:
            self.append_guests(guests_which_want_this_hub)
        else:
            guests_which_want_this_hub = list(
                sorted(guests_which_want_this_hub, key=lambda x: x.favorite_host_hubs[0]["distance"]))
            self.append_guests(guests_which_want_this_hub[0:self.max_guests_left])

    def export_hub(self):
        # Sort guests by distance to the center of the hub so that
        # the closest guests are assigned first
        for guest in self.guests_taken:
            distance = 0
            for zip_string in self.zip_strings:
                distance += db_query.get_zip_distance(zip_string_1=guest.zip_string, zip_string_2=zip_string)
            distance /= float(len(self.zip_strings))
            guest.distance_to_hub = distance

        self.guests_taken = sorted(self.guests_taken, key=lambda x: x.distance_to_hub)

        # Looping through hosts in a circle increasing each host
        # that is not full yet by one guest
        host_index = 0
        guest_index = 0

        # Iterating through all guests assigned to this hub
        while guest_index < len(self.guests_taken):
            guest = self.guests_taken[guest_index]
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

        for guest in Guest.instances:
            guest.remove_host_hub_from_favorites(self)
        HostHub.instances.remove(self)

    def __repr__(self):
        return f"HostHub(Zip String: {self.zip_strings}, Hosts: {len(self.hosts)}, Guests: {len(self.guests_taken)}, MaxGuests: {self.max_guests_left})"

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
    def distribute():
        for host_hub in HostHub.instances:
            host_hub.initial_take()

    @staticmethod
    def export_hubs():
        for host_hub in HostHub.instances:
            CustomLogger.debug(
                f"Exporting HostHub at {host_hub.zip_strings}: {len(host_hub.guests_taken)} guests and {len(host_hub.hosts)} hosts")
            host_hub.export_hub()


class OptimizerMoritz04(Optimizer):

    @staticmethod
    def optimize():

        CustomLogger.info(f"#3A Creating HostHubs: {len(Host.instances)} hosts ...")
        time1 = time()
        HostHub.create_hubs()
        CustomLogger.info(f"#3A Creating HostHubs: Done ({round(time() - time1, 6)} seconds).")

        CustomLogger.info(
            f"#3B Determining each Guest's favorite HostHubs: {len(Guest.instances)} guests and {len(HostHub.instances)} host hubs ({len(Host.instances)} hosts) ...")
        time1 = time()
        OptimizerMoritz04.determine_favorite_host_hubs()
        CustomLogger.info(f"#3B Determining each Guest's favorite HostHubs: Done ({round(time() - time1, 6)} seconds).")

        CustomLogger.info(
            f"#3C Determining each HostHub's favorite Guets: {len(Guest.instances)} guests and {len(HostHub.instances)} host hubs ({len(Host.instances)} hosts) ...")
        time1 = time()
        OptimizerMoritz04.determine_favorite_guests()
        CustomLogger.info(f"#3C Determining each HostHub's favorite Guets: Done ({round(time() - time1, 6)} seconds).")

        CustomLogger.info(f"#3D Initial Take ...")
        time1 = time()
        HostHub.distribute()
        CustomLogger.info(f"#3D Initial Take: Done ({round(time() - time1, 6)} seconds).")

        CustomLogger.info(f"#3E Exporting HostHubs ...")
        time1 = time()
        HostHub.export_hubs()
        CustomLogger.info(f"#3E Exporting HostHubs: Done ({round(time() - time1, 6)} seconds).")

    @staticmethod
    def determine_favorite_host_hubs():
        for guest in Guest.instances:
            favorite_host_hubs = []
            for host_hub in HostHub.instances:
                distance = 0
                for zip_string in host_hub.zip_strings:
                    distance += db_query.get_zip_distance(zip_string_1=guest.zip_string, zip_string_2=zip_string)
                distance = round(distance / float(len(host_hub.zip_strings)), 3)
                favorite_host_hubs.append({"hub": host_hub, "distance": distance})

            favorite_host_hubs = list(sorted(favorite_host_hubs, key=lambda x: x["distance"]))
            guest.favorite_host_hubs = favorite_host_hubs

            CustomLogger.debug("Guests favorite_host_hubs",
                               data_dict={"favorite_host_hubs": [str(type(host)) for host in guest.favorite_host_hubs]})

    @staticmethod
    def determine_favorite_guests():

        for host_hub in HostHub.instances:

            favorite_guests = []

            for guest in Guest.instances:
                distance = list(filter(lambda x: x["hub"] == host_hub, guest.favorite_host_hubs))[0]["distance"]
                favorite_guests.append({"guest": guest, "distance": distance})

            favorite_guests = sorted(favorite_guests, key=lambda x: x["distance"])
            host_hub.favorite_guests = favorite_guests

            CustomLogger.debug("Guests favorite_host_hubs",
                               data_dict={"favorite_host_hubs": [str(guest) for guest in host_hub.favorite_guests]})

            if len(host_hub.favorite_guests) != len(Guest.instances):
                CustomLogger.warning("Guest does not have all HostHubs listed as his favorite hubs.",
                                     data_dict={"Number of Guest.instances": len(Guest.instances),
                                                "Number of favorite_guests": len(host_hub.favorite_guests),
                                                "favorite_guests": host_hub.favorite_guests})
