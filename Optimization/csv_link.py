
import csv
from Optimization.attendee import Host, Guest

from Helpers.custom_printing import CustomPrinting
from Helpers.custom_logger import CustomLogger

from time import time

def load_models(input_file):
    """
        This method takes an 'input_file' (csv) and initializes all Host
        and Guest classes based on the data inside that table
    """
    CustomLogger.info("#1 Loading Models ...")
    time1 = time()

    with open(input_file, newline='') as csvfile:
        rows = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in rows:

            # Skip first row
            if row[0] == 'Region':
                continue

            try:
                number_string = ""
                for character in str(row[3]):
                    if 48 <= ord(character) <= 57:
                        number_string += character
                    else:
                        break
                max_guests = int(number_string)
                max_guests = 4 if max_guests < 4 else max_guests  # Has to be at least 4
            except ValueError:
                max_guests = 4

            kwargs = {
                "region": row[0],
                "allergies": row[2],
                "max_guests": max_guests,
                "street_and_number": row[6],
                "zip_code_and_city": row[7],
                "name": row[4] + " " + row[5],
                "mail": row[8],
                "phone_number": row[9],
                "semester": row[10]
            }

            if row[1] == 'Ja':
                # Pass parameters
                Host(True, **kwargs)
            else:
                # Pass parameters
                Guest(False, **kwargs)

    CustomLogger.info(f"#1 Loading Models: Done ({round(time() - time1, 6)} seconds).")


def export_models(output_file):
    """
        This method takes all all existing Host and Guest classes,
        exports all Host-Guest-Groups in a readable way and stores
        this inside a csv table at the location of 'output_file'.
    """
    CustomLogger.info(f"#4 Exporting Models ...")
    time1 = time()

    rows = [["MATCHED GROUPS GUESTS"]]
    for host in filter(lambda x: x.host, Host.instances):
        rows += host.csv_row_representation()

    rows.append(["GUESTS WITH NO MATCH"])
    for guest in filter(lambda x: x.host is None, Guest.instances):
        rows.append(guest.contact.unmatched_guest_row_representation())

    with open(output_file, 'wt') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(rows)

    CustomLogger.info(f"#4 Exporting Models: Done ({round(time() - time1, 6)} seconds).")
