import csv
from Optimization.attendee import Host, Guest


class Optimization:

    def __init__(self, input_file="Source/in.csv", output_file="Source/out.csv"):
        self.input_file = input_file
        self.output_file = output_file

        self.load_models()
        print(Host.instances)
        print(Guest.instances)

    def load_models(self):
        with open(self.input_file, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
            print(spamreader)
            print("\n\n")
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

    def execute(self):
        return True, ""
