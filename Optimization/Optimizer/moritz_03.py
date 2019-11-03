from Optimization.Optimizer import Optimizer
from Optimization.attendee import Host, Guest

from Helpers.custom_logger import CustomLogger
from Helpers.custom_printing import CustomPrinting

import Database.queries as db_query

from time import time


class HostHub:
    MAX_DISTANCE_BETWEEN_HOSTS = 500

    instances = []

    def __init__(self):
        self.hosts = []

        self.guests_taken = []
        self.max_guests_left = 0
        self.favorite_guests = []
        self.filled_up = True

        self.zip_strings = []
        HostHub.instances.append(self)

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
        self.filled_up = self.max_guests_left <= 0

    def append_guests(self, appendix):
        if isinstance(appendix, Guest):
            self.guests_taken.append(appendix)
            self.max_guests_left -= 1
            appendix.assigned_to_hub = True
        elif isinstance(appendix, list):
            self.guests_taken += appendix
            self.max_guests_left -= len(appendix)
            for guest in appendix:
                guest.assigned_to_hub = True

    def export_hub(self):

        # Looping through hosts in a circle increasing each host
        # that is not full yet by one guest
        guest_index = 0

        CustomLogger.debug(f"Exporting HostHub at {self.zip_strings}: {len(self.guests_taken)} guests and {len(self.hosts)} hosts")

        CustomLogger.debug(f"Iterating through hosts:", data_dict={
            "Hosts": [str(x) for x in self.hosts],
        })

        for host in self.hosts:
            guests_to_append = self.guests_taken[guest_index:guest_index+host.max_guests]

            CustomLogger.debug("Assigning guests to hosts:", data_dict={
                "Host": str(host),
                "Number of guests to append": len(guests_to_append),
                "Guests to append": [str(x) for x in guests_to_append]
            })

            host.append_guests(guests_to_append)
            guest_index += host.max_guests

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
    def update_hub_lists():
        for host_hub in HostHub.instances:
            if host_hub.max_guests_left <= 0:
                host_hub.filled_up = True
                for guest in Guest.instances:
                    guest.remove_host_hubs_from_favorites(host_hub)
            else:
                host_hub.filled_up = False

    @staticmethod
    def export_hubs():
        CustomLogger.debug("Exporting Hubs:", data_dict={
            "Number of HostHubs": len(HostHub.instances),
            "HostHubs": [str(x) for x in HostHub.instances]
        })

        for host_hub in HostHub.instances:
            host_hub.export_hub()

        HostHub.instances = []



class OptimizerMoritz03(Optimizer):

    @staticmethod
    def optimize():

        CustomLogger.info(f"#3.1 Creating HostHubs: {len(Host.instances)} hosts ...")
        time1 = time()
        HostHub.create_hubs()
        CustomLogger.info(f"#3.1 Creating HostHubs: Done ({round(time() - time1, 6)} seconds).")

        CustomLogger.info(f"#3.2 Determining each Guest's favorite HostHubs: {len(Guest.instances)} guests and {len(HostHub.instances)} host hubs ({len(Host.instances)} hosts) ...")
        time1 = time()
        OptimizerMoritz03.determine_favorite_host_hubs()
        CustomLogger.info(f"#3.2 Determining each Guest's favorite HostHubs: Done ({round(time() - time1, 6)} seconds).")

        CustomLogger.info(f"#3.3 Distributing Guests ...")
        time1 = time()
        OptimizerMoritz03.distribute_guests()
        CustomLogger.info(f"#3.3 Distributing Guests: Done ({round(time() - time1, 6)} seconds).")

        CustomLogger.info(f"#3.4 Exporting HostHubs ...")
        time1 = time()
        HostHub.export_hubs()
        CustomLogger.info(f"#3.4 Exporting HostHubs: Done ({round(time() - time1, 6)} seconds).")

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

            # CustomLogger.debug("Guests favorite_host_hubs", data_dict={"favorite_host_hubs": [[str(x["hub"]), x["distance"]] for x in guest.favorite_host_hubs]})

    @staticmethod
    def distribute_guests():
        round_number = 1

        while True:

            guests_without_hub = list(filter(lambda x: not x.assigned_to_hub, Guest.instances))
            hubs_with_free_spots = list(filter(lambda x: not x.filled_up, HostHub.instances))

            CustomLogger.debug(f"Distributing Guests -> Round {round_number} ({len(guests_without_hub)} free guests and {len(hubs_with_free_spots)} free hosts)",
                               data_dict={
                                   "guests_without_hub": [str(x) for x in guests_without_hub],
                                   "hubs_with_free_spots": [str(x) for x in hubs_with_free_spots],
                               })
            round_number += 1

            if len(guests_without_hub) == 0 or len(hubs_with_free_spots) == 0:
                break

            for host_hub in hubs_with_free_spots:
                guests_which_want_this_hub = []
                for guest in guests_without_hub:
                    if guest.favorite_host_hub().zip_strings == host_hub.zip_strings:
                        guests_which_want_this_hub.append(guest)

                if len(guests_which_want_this_hub) <= host_hub.max_guests_left:
                    guests_to_be_assigned = guests_which_want_this_hub
                else:
                    guests_which_want_this_hub = list(sorted(guests_which_want_this_hub, key=lambda x: x.favorite_host_hub_distance()))
                    guests_to_be_assigned = guests_which_want_this_hub[0:host_hub.max_guests_left]

                CustomLogger.debug(f"{str(host_hub)}:", data_dict={
                    "guests_which_want_this_hub": len(guests_which_want_this_hub),
                    "max_guests_left": int(host_hub.max_guests_left),
                    "guests_to_be_assigned": len(guests_to_be_assigned)
                })

                CustomLogger.debug(f"{str(host_hub)}: before appending", data_dict={
                    "guests_taken": len(host_hub.guests_taken),
                    "max_guests_left": host_hub.max_guests_left
                })

                host_hub.append_guests(guests_to_be_assigned)

                CustomLogger.debug(f"{str(host_hub)}: after appending", data_dict={
                    "guests_taken": len(host_hub.guests_taken),
                    "max_guests_left": host_hub.max_guests_left
                })

            HostHub.update_hub_lists()




