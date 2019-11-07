import csv
from tqdm import tqdm

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from secrets import OUTLOOK_CREDENTIALS_USER, OUTLOOK_CREDENTIALS_PASS, OUTLOOK_FROM_EMAIL, OUTLOOK_TO_EMAIL



def get_message_batch_1_guest(name="<insert_name_here>"):
    message = f"Servus {name}," \
              "\n\n" \
              "auf dich wartet ein super entspannter Abend mit deinen Kommilitonen!" \
              "\n\n" \
              "Das Beste daran ist, du musst nichts weiter tun, als dir den 12.11.um " \
              "18:30 Uhr in deinen Kalender einzutragen." \
              "\n\n" \
              "Doch welche Leute in deiner Gruppe sind, halten wir bis zum Ende geheim, " \
              "damit die Spannung nicht verloren geht. Die Adressdaten des Gastgebers " \
              "werden wir dir dann am Tag vor dem Event noch per Mail mitteilen." \
              "\n\n" \
              "Dein MSEating Team"
    return message


def get_message_batch_1_host(name="<insert_name_here>", number_of_guests=0, food_requirements=[]):
    # number_of_guests now includes the host itself
    number_of_guests += 1

    # Rezeptvorschläge anhängen???

    if len(food_requirements) == 0:
        food_requirements_string = "Deine Gäste haben KEINE Essensbesonderheiten angegeben."
    else:
        food_requirements_string = "Deine Gäste haben folgende Essensbesonderheiten:\n"
        for food_requirement in food_requirements:
            food_requirements_string += f"\t* {food_requirement}\n"

    message = f"Servus {name} - Du hast gewonnen!" \
              "\n\n" \
              "Und zwar einen super entspannten Abend mit deinen Kommilitonen!" \
              "\n\n" \
              "Das Beste daran ist - du musst nicht mal irgendwo hinfahren, sondern " \
              "das Event findet direkt bei dir zu Hause statt und zwar am 12.11. um 18:30." \
              "\n\n" \
              f"Du kannst mit {number_of_guests} Personen (inkl. dir) rechnen. Damit du auf " \
              f"keinen Kosten sitzenbleibst, kannst du den Teilnehmerbeitrag von {number_of_guests * 7}€ " \
              f"({number_of_guests} x 7€) deiner Abendgenossen (und dir) ab sofort im " \
              f"Fachschaftsraum abholen." \
              "\n\n" \
              "Was du dann letztendlich machst - also was du kochen willst  - kannst " \
              "du ganz allein entscheiden. Dabei kannst du dich entweder an den Rezept" \
              "vorschlägen unten orientieren, oder du kochst einfach dein Lieblingsgericht!" \
              "\n\n" \
              f"{food_requirements_string}" \
              "\n" \
              "Bitte hänge am Tag der Veranstaltung einen Zettel an deine Klingel mit der " \
              "Aufschrift „MSEating“, da deine Gäste deinen Namen ja (noch) nicht kennen werden! " \
              "Wir melden uns dann einen Tag vor dem Abend nochmal." \
              "\n\n" \
              "Dein MSEating - Team"
    return message


def get_attendees_list(input_file="out.csv"):
    attendees_list = []
    with open(input_file, newline='') as csvfile:
        rows = csv.reader(csvfile, delimiter=',', quotechar='|')
        host_index = -1
        for row in rows:
            if len(row) < 2:
                continue
            name_and_type = row[0]
            if name_and_type[-4:] == "ost)":
                # This row belongs to a host
                host_index += 1
                address = row[1].replace("\"", "").replace("\u00df", "ss") + "," + row[2].replace("\"", "").replace("\u00fc", "ue")
                attendees_list.append({"name": name_and_type[:-7],
                                       "number_of_guests": 0,
                                       "food_requirements": [],
                                       "address": address,
                                       "mail": row[4],
                                       "phone": row[5],
                                       "guests": []})
            else:
                if name_and_type[-7:] == "(Guest)":
                    # This row belongs to a matched guest
                    attendees_list[host_index]["guests"].append({"name": name_and_type[:-8],
                                                                 "mail": row[3],
                                                                 "phone": row[4],
                                                                 "food_requirements": row[1][11:]})
                    if row[1][11:] != "None":
                        attendees_list[host_index]["food_requirements"].append(row[1][11:])
                    attendees_list[host_index]["number_of_guests"] += 1

    return attendees_list


def send_mails_batch_1(input_file="out.csv"):
    attendees_list = get_attendees_list(input_file=input_file)
    mails = []
    for host in attendees_list:
        message = get_message_batch_1_host(name=host["name"],
                                           number_of_guests=host["number_of_guests"],
                                           food_requirements=host["food_requirements"])
        mail_address = host["mail"]
        mails.append({"mail_address": mail_address, "subject": "You made it!", "message": message})
        for guest in host["guests"]:
            message = get_message_batch_1_guest(name=guest["name"])
            mail_address = guest["mail"]
            mails.append({"mail_address": mail_address, "subject": "You made it!", "message": message})

    send_mails(mails)


def send_mails(mails):

    # Just for testing
    if len(mails) > 10:
        mail_count = 10
    else:
        mail_count = len(mails)

    # Set up the SMTP server
    s = smtplib.SMTP(host='postout.lrz.de', port=587)
    s.starttls()
    s.login(OUTLOOK_CREDENTIALS_USER, OUTLOOK_CREDENTIALS_PASS)

    # for i in tqdm(range(len(mails))):
    for i in tqdm(range(mail_count)):
        print("#"*10 + f"Sending Mail to {mails[i]['mail_address']}" + "#"*10)

        # Set up message
        msg = MIMEMultipart()
        msg['From'] = OUTLOOK_FROM_EMAIL
        msg['To'] = OUTLOOK_TO_EMAIL  # mails[i]["mail_address"]
        msg['Bcc'] = ""
        msg['Subject'] = mails[i]["subject"]
        msg.attach(MIMEText(mails[i]["message"].replace("\n", "<br/>"), 'html'))

        # Send message
        s.send_message(msg)

        del msg


if __name__ == "__main__":
    send_mails_batch_1()
