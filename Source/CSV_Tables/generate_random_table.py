import random
import csv

# Source for zip codes https://www.suche-postleitzahl.org/muenchen-plz-80331-85540.52bb
ZIP_CODES = [80995, 80997, 80999, 81247, 81249,
             80331, 80333, 80335, 80336, 80469, 80538, 80539,
             81541, 81543, 81667, 81669, 81671, 81675, 81677,
             81241, 81243, 81245, 81249,
             81671, 81673, 81677, 81735, 81825, 81829,
             81675, 81677, 81679, 81925, 81927, 81929,
             80933, 80935, 80995,
             80689, 81375, 81377,
             80639, 80686, 80687, 80689,
             80331, 80335, 80336, 80337, 80339, 80469, 80538,
             80333, 80335, 80539, 80636, 80797, 80798, 80799, 80802,
             80797, 80807, 80809, 80933, 80935, 80937, 80939,
             80637, 80638, 80992, 80993, 80995, 80997,
             80335, 80634, 80636, 80637, 80638, 80639, 80797, 80809, 80992,
             81539, 81541, 81547, 81549,
             80687, 80689, 80992, 80997, 81241, 81243, 81245, 81247, 81249,
             81539, 81541, 81549, 81669, 81671, 81735, 81737, 81739, 81827,
             80538, 80539, 80799, 80801, 80802, 80803, 80804, 80805, 80807, 80939,
             80796, 80797, 80798, 80799, 80801, 80803, 80804, 80809,
             80335, 80339,
             80336, 80337, 81369, 81371, 81373, 81379,
             80686, 81369, 81373, 81377, 81379,
             81369, 81371, 81379, 81475, 81476, 81477, 81479,
             81735, 81825, 81827, 81829, 85540,
             81539, 81543, 81545, 81547, 81549]

if __name__ == "__main__":

    rows = [["Region", "Host", "Allergies", "Max Guests", "Vorname", "Nachname", "Straße und Hausnummer", "Postleitzahl und Ort", "TUM Mail", "Handynummer", "Semester", "Einwilligung in Daten-Weitergabe"]]

    for i in range(500):
        host = "Ja" if random.randint(1, 5) == 1 else "Nein"
        zip_code = random.choice(ZIP_CODES)
        row = ["Innenstadt", host, "<allergies>", "<max_guests>", "<vorname>", "<nachname>", "Straße 4", f"{zip_code} München", "<mail_address>", "<phone_number>", "<semester>", "Ja"]
        rows.append(row)

    with open("generic_example.csv", 'wt') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(rows)
