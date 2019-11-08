from Optimization.Optimizer import Optimizer
from Optimization.attendee import Host, Guest

from Helpers.custom_logger import CustomLogger

import Database.queries as db_query

from time import time


class HostHub:
    MAX_DISTANCE_BETWEEN_HOSTS = 500

    instances = []

    def __init__(self, zip_string):

        self.hosts = []
        self.guests_taken = []

        self.max_guests_left = 0
        self.filled_up = True

        self.zip_string = zip_string
        HostHub.instances.append(self)

    def append_host(self, host):
        self.hosts.append(host)
        self.max_guests_left += host.max_guests
        self.filled_up = self.max_guests_left <= 0

    def append_guests(self, guests):
        self.guests_taken += guests
        self.max_guests_left -= len(guests)
        for guest in guests:
            guest.assigned_to_hub = True
            guest.distance_to_hub = OptimizerMoritz05.zip_distances[guest.zip_string][self.zip_string]
            guest.hub = self

        if self.max_guests_left <= 0:
            self.filled_up = True

    def export_hub(self):

        # Looping through hosts in a circle increasing each host
        # that is not full yet by one guest
        guest_index = 0

        CustomLogger.debug(f"Exporting HostHub at {self.zip_string}: {len(self.guests_taken)} guests and {len(self.hosts)} hosts")

        CustomLogger.debug(f"Iterating through hosts:", data_dict={
            "Hosts": [str(x) for x in self.hosts],
        })

        for host in self.hosts:
            guests_to_append = self.guests_taken[guest_index:guest_index+host.max_guests]

            CustomLogger.debug("Assigning guests to hosts:", data_dict={
                "Host": str(host),
                "Number of guests to append": len(guests_to_append)
            })

            host.append_guests(guests_to_append)
            guest_index += host.max_guests

    def __repr__(self):
        return f"HostHub(Zip String: {self.zip_string}, Hosts: {len(self.hosts)}, Guests: {len(self.guests_taken)}, MaxGuests: {self.max_guests_left})"


    @staticmethod
    def create_hubs():
        for host in Host.instances:
            added_to_hub = False
            for host_hub in HostHub.instances:
                if host_hub.zip_string == host.zip_string:
                    host_hub.append_host(host)
                    added_to_hub = True
                    CustomLogger.debug(f"Extended HostHub at {host_hub.zip_string}")
                    break
            if not added_to_hub:
                new_host_hub = HostHub(host.zip_string)
                new_host_hub.append_host(host)
                CustomLogger.debug(f"New HostHub at {new_host_hub.zip_string}")

    @staticmethod
    def update_hub_lists():
        host_hubs = list(filter(lambda hub: hub.max_guests_left <= 0, HostHub.instances))
        for guest in Guest.instances:
            guest.remove_host_hubs_from_favorites(host_hubs)

    @staticmethod
    def export_hubs():
        CustomLogger.debug("Exporting Hubs:", data_dict={
            "Number of HostHubs": len(HostHub.instances),
            "HostHubs": [str(x) for x in HostHub.instances]
        })

        for host_hub in HostHub.instances:
            host_hub.export_hub()

        HostHub.instances = []



class OptimizerMoritz05(Optimizer):

    zip_distances = {}

    @staticmethod
    def optimize():

        CustomLogger.info(f"#3.1 Creating HostHubs: {len(Host.instances)} hosts ...")
        time1 = time()
        HostHub.create_hubs()
        CustomLogger.info(f"#3.1 Creating HostHubs: Done ({round(time() - time1, 6)} seconds).")

        CustomLogger.info(f"#3.2 Determining each Guest's favorite HostHubs: {len(Guest.instances)} guests and {len(HostHub.instances)} host hubs ({len(Host.instances)} hosts) ...")
        time1 = time()
        OptimizerMoritz05.determine_favorite_host_hubs()
        CustomLogger.info(f"#3.2 Determining each Guest's favorite HostHubs: Done ({round(time() - time1, 6)} seconds).")

        CustomLogger.info(f"#3.3 Distributing Guests ...")
        time1 = time()
        OptimizerMoritz05.distribute_guests()
        CustomLogger.info(f"#3.3 Distributing Guests: Done ({round(time() - time1, 6)} seconds).")

        CustomLogger.info(f"#3.4 Switching Guests ...")
        time1 = time()
        OptimizerMoritz05.switch_guests()
        CustomLogger.info(f"#3.4 Switching Guests: Done ({round(time() - time1, 6)} seconds).")

        CustomLogger.info(f"#3.5 Exporting HostHubs ...")
        time1 = time()
        HostHub.export_hubs()
        CustomLogger.info(f"#3.5 Exporting HostHubs: Done ({round(time() - time1, 6)} seconds).")

        for guest in list(filter(lambda x: x.assigned_to_hub, Guest.instances)):
            distance = OptimizerMoritz05.zip_distances[guest.zip_string][guest.host.zip_string]
            guest.distance_to_hub = distance


    @staticmethod
    def get_zip_distance(zip_string_1, zip_string_2):
        """
        Storing the used zip-distances in a table is way more efficient than
        querying the database every single time!
        """
        try:
            distance = OptimizerMoritz05.zip_distances[zip_string_1][zip_string_2]
        except KeyError:
            distance = db_query.get_zip_distance(zip_string_1=zip_string_1, zip_string_2=zip_string_2)
            if zip_string_1 not in OptimizerMoritz05.zip_distances:
                OptimizerMoritz05.zip_distances[zip_string_1] = {zip_string_2: distance}
            else:
                OptimizerMoritz05.zip_distances[zip_string_1][zip_string_2] = distance
            if zip_string_2 not in OptimizerMoritz05.zip_distances:
                OptimizerMoritz05.zip_distances[zip_string_2] = {zip_string_1: distance}
            else:
                OptimizerMoritz05.zip_distances[zip_string_2][zip_string_1] = distance
        return distance


    @staticmethod
    def determine_favorite_host_hubs():
        for guest in Guest.instances:
            favorite_host_hubs = [(hub, OptimizerMoritz05.get_zip_distance(hub.zip_string, guest.zip_string)) for hub in HostHub.instances]
            favorite_host_hubs = list(sorted(favorite_host_hubs, key=lambda x: x[1]))
            guest.favorite_host_hubs = favorite_host_hubs


    @staticmethod
    def distribute_guests():
        round_number = 1

        while True:

            guests_without_hub = list(filter(lambda x: not x.assigned_to_hub, Guest.instances))
            hubs_with_free_spots = list(filter(lambda x: not x.filled_up, HostHub.instances))

            CustomLogger.debug(
                f"Distributing Guests -> Round {round_number} ({len(guests_without_hub)} free guests and {len(hubs_with_free_spots)} free hosts)")

            """
            CustomLogger.debug(f"Distributing Guests -> Round {round_number} ({len(guests_without_hub)} free guests and {len(hubs_with_free_spots)} free hosts)",
                               data_dict={
                                   "guests_without_hub": [str(x) for x in guests_without_hub],
                                   "hubs_with_free_spots": [str(x) for x in hubs_with_free_spots],
                               })
            """

            round_number += 1

            if len(guests_without_hub) == 0 or len(hubs_with_free_spots) == 0:
                break

            for host_hub in hubs_with_free_spots:
                guests_which_want_this_hub = list(filter(lambda x: x.favorite_host_hub() == host_hub, guests_without_hub))

                if len(guests_which_want_this_hub) <= host_hub.max_guests_left:
                    guests_to_be_assigned = guests_which_want_this_hub
                else:
                    guests_which_want_this_hub = list(sorted(guests_which_want_this_hub,
                                                             key=lambda x: x.favorite_host_hub_distance()))
                    guests_to_be_assigned = guests_which_want_this_hub[0:host_hub.max_guests_left]

                """
                
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
                
                """

                host_hub.append_guests(guests_to_be_assigned)

            HostHub.update_hub_lists()


    @staticmethod
    def switch_guests():
        round_number = 0

        average_travel_distance = 0

        while True:

            matched_guests = list(filter(lambda x: x.assigned_to_hub, Guest.instances))
            matched_guests = list(sorted(matched_guests, key=lambda x: x.distance_to_hub))

            new_average_travel_distance = 0
            for guest in matched_guests:
                new_average_travel_distance += guest.distance_to_hub
            new_average_travel_distance /= len(matched_guests)

            guests_with_long_distances = list(filter(lambda x: x.distance_to_hub > 1.5 * new_average_travel_distance, matched_guests))

            if round_number == 0:
                CustomLogger.info(f"Starting Brute-Force-Approach @ average_travel_distance = {round(new_average_travel_distance, 6)} meters")

            # At least 10 itearations
            # stop iterating, when optimization is not converging anymore
            # At most 100 iterations
            if round_number > 10:
                if round_number >= 100 or round(new_average_travel_distance, 6) == round(average_travel_distance, 6):
                    # If the maximum number of rounds is reached OR the optimization does not converge anymore
                    CustomLogger.info(f"Finished Brute-Force-Approach after round {round_number} @ average_travel_distance = {round(new_average_travel_distance, 6)} meters")
                    break

            average_travel_distance = new_average_travel_distance
            round_number += 1

            CustomLogger.debug(
                f"Switching Guests -> Round {round_number} ({len(matched_guests) - len(guests_with_long_distances)} " +
                f"short_routed_guests, {len(guests_with_long_distances)} long_routed_guests @ " +
                f"average_travel_distance = {round(average_travel_distance, 6)} meters)")

            switched_guests = []

            for unlucky_guest in guests_with_long_distances[::]:
                # Determine the partner where the switch is best
                saved_distance_when_switched = 0
                switch_partner = None

                if unlucky_guest in switched_guests:
                    # Only try to switch participants that haven't been switched
                    # in this round -> Super weird convergence without this
                    continue

                for lucky_guest in matched_guests:

                    if unlucky_guest.hub == lucky_guest.hub or lucky_guest in switched_guests:
                        # Do not try to switch guests within one guest hub -> save power

                        # Only try to switch participants that haven't been switched
                        # in this round -> Super weird convergence without this
                        continue

                    distance_before_switch = unlucky_guest.distance_to_hub + lucky_guest.distance_to_hub

                    new_possible_distance_of_unlucky_guest = OptimizerMoritz05.zip_distances[unlucky_guest.zip_string][lucky_guest.hub.zip_string]
                    new_possible_distance_of_lucky_guest = OptimizerMoritz05.zip_distances[lucky_guest.zip_string][unlucky_guest.hub.zip_string]
                    distance_after_switch = new_possible_distance_of_unlucky_guest + new_possible_distance_of_lucky_guest

                    if (distance_before_switch - distance_after_switch) > saved_distance_when_switched:
                        switch_partner = lucky_guest
                        saved_distance_when_switched = distance_before_switch - distance_after_switch

                if switch_partner is not None:
                    # Actually switch spots

                    # Prevent these two participants to take part in another switch this round
                    switched_guests.append(unlucky_guest)
                    switched_guests.append(switch_partner)

                    # Change each guest's hub reference
                    unlucky_guest.hub, switch_partner.hub = switch_partner.hub, unlucky_guest.hub

                    # Changes each guest's hub's guest list
                    unlucky_guest.hub.guests_taken.remove(switch_partner)
                    unlucky_guest.hub.guests_taken.append(unlucky_guest)
                    switch_partner.hub.guests_taken.remove(unlucky_guest)
                    switch_partner.hub.guests_taken.append(switch_partner)

                    # Change each guest's distance_to_hub value
                    unlucky_guest.distance_to_hub = OptimizerMoritz05.zip_distances[unlucky_guest.zip_string][unlucky_guest.hub.zip_string]
                    switch_partner.distance_to_hub = OptimizerMoritz05.zip_distances[switch_partner.zip_string][switch_partner.hub.zip_string]






















