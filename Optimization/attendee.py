from abc import ABC, abstractmethod
import requests
import json
from Helpers.custom_printing import CustomPrinting
from Helpers.custom_math import CustomMath

region_zip_codes = {
    "Innenstadt": "80333",
    "Garching + Freimann": "80939",
    "Westen + Norden": "80995",
    "Süden + Osten": "81737",
    "München": "80539"
}

class Contact:

    def __init__(self, attendee, name="", region="", street_and_number="", allergies="", mail="", phone_number="", semester=""):
        self.attendee = attendee

        self.name = name
        self.region = region
        self.street_and_number = street_and_number

        self.allergies = allergies
        self.mail = mail
        self.phone_number = phone_number
        self.semester = semester


class Attendee(ABC):

    ids_free = range(512)
    ids_used = []

    def __init__(self, host, max_people="",
                 region="", street_and_number="", zip_code_and_city="",
                 name="", allergies="", mail="", phone_number="", semester=""):

        self.host = host  # In case there are too many hosts
        self.max_people = max_people

        self.lat = 0
        self.lng = 0
        self.get_coordinates(region, street_and_number, zip_code_and_city)

        self.contact = Contact(self, name=name, region=region, street_and_number=street_and_number,
                               allergies=allergies, mail=mail, phone_number=phone_number, semester=semester)

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

        # Get Latitude an Longitude from Google Maps API
        request_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={zip_string}+München&key=AIzaSyCIFTVJuD_NRITAuxlIWYKIhnTzCBIr0wQ"
        CustomPrinting.print_yellow(f"Now requesting: GET => {request_url}")
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


class Host(Attendee):

    instances = []

    def __init__(self, host, max_people="",
                 region="", street_and_number="", zip_code_and_city="",
                 name="", allergies="", mail="", phone_number="", semester=""):

        super().__init__(host=host, max_people=max_people,
                         region=region, street_and_number=street_and_number, zip_code_and_city=zip_code_and_city,
                         name=name, allergies=allergies, mail=mail, phone_number=phone_number, semester=semester)

        Host.instances.append(self)

    def __repr__(self):
        return f"Host(Name: {self.contact.name}, Coordinates: {round(self.lat, 7)}N, {round(self.lng, 7)}E)"

class Guest(Attendee):

    instances = []

    def __init__(self, host, max_people="",
                 region="", street_and_number="", zip_code_and_city="",
                 name="", allergies="", mail="", phone_number="", semester=""):

        super().__init__(host=host, max_people=max_people,
                         region=region, street_and_number=street_and_number, zip_code_and_city=zip_code_and_city,
                         name=name, allergies=allergies, mail=mail, phone_number=phone_number, semester=semester)

        Guest.instances.append(self)

    def __repr__(self):
        return f"Guest(Name: {self.contact.name}, Coordinates: {round(self.lat, 7)}N, {round(self.lng, 7)}E)"



