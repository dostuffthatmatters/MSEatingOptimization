
import csv
from Optimization.attendee import Host, Guest

def load_models(input_file):
    with open(input_file, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in spamreader:

            # Skip first row
            if row[0] == 'Region':
                continue

            kwargs = {
                "region": row[0],
                "allergies": row[2],
                "max_people": row[3],
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


def export_models(output_file):
    rows = [["MATCHED GROUPS GUESTS"]]

    for host in Host.instances:
        if host.host:
            rows += host.csv_row_representation()

    rows.append(["GUESTS WITH NO MATCH"])

    for guest in Guest.instances:
        if guest.host is None:
            rows.append(guest.contact.unmatched_guest_row_representation())

    with open(output_file, 'wt') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(rows)
