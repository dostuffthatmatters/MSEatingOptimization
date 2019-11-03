from abc import ABC, abstractmethod
import requests
import json

from Helpers.custom_logger import CustomLogger
import Database.queries as db_query
import Database.additions as db_addition

region_zip_codes = {
    "Innenstadt": "80333",
    "Garching + Freimann": "80939",
    "Westen + Norden": "80995",
    "Süden + Osten": "81737",
    "München": "80539"
}

class Contact:

    def __init__(self, attendee, name="", max_guests="", allergies="", semester="",
                 region="", street_and_number="",
                 mail="", phone_number=""):

        self.attendee = attendee

        self.name = name
        self.max_guests = max_guests
        self.allergies = allergies

        self.region = region
        self.street_and_number = street_and_number
        self.zip_code_and_city = ""

        self.mail = mail
        self.phone_number = phone_number
        self.semester = semester

    def host_row_representation(self):
        return [f"{self.name} (Host)", f"{self.street_and_number}, {self.zip_code_and_city}", f"Max. Guests: {self.max_guests}", self.mail, self.phone_number]

    def guest_row_representation(self):
        return [f"{self.name} (Guest)", f"Allergies: {self.allergies if len(self.allergies) > 0 else 'None'}", " ", self.mail, self.phone_number]

    def unmatched_guest_row_representation(self):
        return [f"{self.name} (Unmatched Guest)", f"{self.street_and_number}, {self.zip_code_and_city}", f"Allergies: {self.allergies if len(self.allergies) > 0 else 'None'}", self.mail, self.phone_number]

    @staticmethod
    def empty_row_representation():
        return ["", "", "", ""]



class Attendee(ABC):

    def __init__(self, host, name="", max_guests="", allergies="", semester="",
                 region="", street_and_number="", zip_code_and_city="",
                 mail="", phone_number=""):

        # True if the attendee is a host - needed in case there
        # are too many hosts and some hosts are just guests
        self.host = host

        self.max_guests = max_guests
        self.contact = Contact(self, name=name, max_guests=max_guests, allergies=allergies, semester=semester,
                               region=region, street_and_number=street_and_number,
                               mail=mail, phone_number=phone_number)

        self.lat = 0
        self.lng = 0
        self.zip_string = ""
        self.get_coordinates(region, street_and_number, zip_code_and_city)

    def get_coordinates(self, region, street_and_number, zip_code_and_city):
        zip_string = ""
        for char in zip_code_and_city:
            if 48 <= ord(char) <= 57:
                zip_string += char

        if len(zip_string) != 5:
            if region != "":
                zip_string = region_zip_codes[region]
            else:
                zip_string = region_zip_codes["München"]

        self.contact.zip_code_and_city = zip_string + " München"
        self.zip_string = zip_string

        zip_code_row = db_query.get_zip_code_row(zip_string)

        if zip_code_row is None:
            # Get Latitude an Longitude from Google Maps API
            request_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={zip_string}+München&key=AIzaSyCIFTVJuD_NRITAuxlIWYKIhnTzCBIr0wQ"
            CustomLogger.debug(f"Now requesting from the Geocode API: {zip_string}")
            response = requests.get(request_url)

            try:
                coordinates_dict = json.loads(response.text)["results"][0]["geometry"]["location"]
                self.lat = coordinates_dict["lat"]
                self.lng = coordinates_dict["lng"]
            except KeyError as e:
                print(e)
                # Coordinates of "80539 München" (Center of Munich)
                self.lat = 48.1447027
                self.lng = 11.5821606

            CustomLogger.debug(f"Adding to database: {zip_string} => coords: {self.lat}N, {self.lng}E")
            db_addition.add_zip_code(zip_string, self.lat, self.lng)

        else:
            CustomLogger.debug(f"Now fetching from database: {zip_string}")
            self.lat = zip_code_row.lat
            self.lng = zip_code_row.lng


class Host(Attendee):

    instances = []

    def __init__(self, host, max_guests="",
                 region="", street_and_number="", zip_code_and_city="",
                 name="", allergies="", mail="", phone_number="", semester=""):

        super().__init__(host=host, max_guests=max_guests,
                         region=region, street_and_number=street_and_number, zip_code_and_city=zip_code_and_city,
                         name=name, allergies=allergies, mail=mail, phone_number=phone_number, semester=semester)

        Host.instances.append(self)
        self.guests = []

    def __repr__(self):
        return f"Host(Name: {self.contact.name}, Coordinates: {round(self.lat, 7)}N, {round(self.lng, 7)}E)"

    def csv_row_representation(self):
        rows = [self.contact.host_row_representation()]


        for guest in self.guests:
            rows.append(guest.contact.guest_row_representation())

        rows.append(Contact.empty_row_representation())
        rows.append(Contact.empty_row_representation())
        return rows

    def append_guests(self, guests):
        if isinstance(guests, list):
            self.guests += guests
            for guest in guests:
                guest.host = self
        else:
            self.guests.append(guests)
            guests.host = self


class Guest(Attendee):

    instances = []

    def __init__(self, host, max_guests="",
                 region="", street_and_number="", zip_code_and_city="",
                 name="", allergies="", mail="", phone_number="", semester=""):

        super().__init__(host=host, max_guests=max_guests,
                         region=region, street_and_number=street_and_number, zip_code_and_city=zip_code_and_city,
                         name=name, allergies=allergies, mail=mail, phone_number=phone_number, semester=semester)

        Guest.instances.append(self)
        self.host = None
        self.assigned_to_hub = False

        self.favorite_host_hubs = []

    def __repr__(self):
        return f"Guest(Name: {self.contact.name}, Zip: {self.zip_string}, Assigned to Hub: {self.assigned_to_hub}, Host: {self.host})"

    def switch_host_hub(self, instance_list):
        if len(self.favorite_host_hubs) != 0:
            self.favorite_host_hubs.pop(0)

        if len(self.favorite_host_hubs) != 0:
            new_host_hub = self.favorite_host_hubs[0]["hub"]
            if new_host_hub in instance_list and not new_host_hub.filled_up():
                new_host_hub.append_guests(self)
            else:
                self.switch_host_hub(instance_list)

    def distance_to_next_free_host_hub(self):
        for host_hub in self.favorite_host_hubs:
            if not host_hub["hub"].filled_up():
                return host_hub["distance"]
        return 100000

    def remove_host_hubs_from_favorites(self, host_hub_s):
        if isinstance(host_hub_s, list):
            self.favorite_host_hubs = list(filter(lambda x: x["hub"] not in host_hub_s, self.favorite_host_hubs))
        else:
            self.favorite_host_hubs = list(filter(lambda x: x["hub"] != host_hub_s, self.favorite_host_hubs))

    def favorite_host_hub(self):
        return self.favorite_host_hubs[0]["hub"]

    def favorite_host_hub_distance(self):
        return self.favorite_host_hubs[0]["distance"]
