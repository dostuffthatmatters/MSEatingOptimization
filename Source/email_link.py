import csv
from tqdm import tqdm

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from secrets import OUTLOOK_CREDENTIALS_USER, OUTLOOK_CREDENTIALS_PASS,\
    OUTLOOK_FROM_EMAIL, OUTLOOK_TO_EMAIL, OUTLOOK_REPLY_TO_ADDRESS,\
    MSE_EMERGENCY_PHONE_NUMBERS, SMTP_SERVER, SMTP_PORT


def get_message_batch_1_guest(name="<insert_name_here>"):
    name = name.split(" ")[0]
    message = f"Servus {name}," \
              "\n\n" \
              "auf dich wartet ein super entspannter Abend mit deinen Kommilitonen!" \
              "\n\n" \
              "Das Beste daran ist, du musst nichts weiter tun, als dir den 12.11. um " \
              "18:30 Uhr in deinen Kalender einzutragen." \
              "\n\n" \
              "Doch welche Leute in deiner Gruppe sind, halten wir bis zum Ende geheim, " \
              "damit die Spannung nicht verloren geht. Die Adressdaten des Gastgebers " \
              "werden wir dir dann am Tag vor dem Event noch per Mail mitteilen." \
              "\n\n" \
              "Dein MSEating Team"
    return message


def get_message_batch_2_guest(name="<insert_name_here>", address="", phone_number=""):
    name = name.split(" ")[0]

    emergency_list = ""
    for emergency_name in MSE_EMERGENCY_PHONE_NUMBERS:
        emergency_list += "\n\t* " + emergency_name + ": " + MSE_EMERGENCY_PHONE_NUMBERS[emergency_name]

    message = f"Servus {name}," \
              "\n\n" \
              "morgen ist es endlich soweit. Da du bislang immer noch keine Ahnung hast, " \
              "wo du den Abend verbringen wirst, hier die Adresse von deinem Chefkoch-Gastgeber:\n" \
              f"<strong>{address}</strong>" \
              "\n\n" \
              "Also erscheine morgen pünktlich um 18:30 vor ihrer/seiner Haustür. An der Klingel " \
              "wird ein MSEating Schild hängen." \
              "\n\n" \
              "Viel Spaß bei der Suche!!" \
              "\n\n" \
              "Dein MSEating Team" \
              "\n\n" \
              "PS: Falls du Probleme haben solltest, kannst du uns gerne anrufen:" \
              f"{emergency_list}" \
              "\n\n"\
              "(und denk daran: es gibt auch Googlemaps  & die  MVG-App ;P)"
    return message


def get_message_batch_1_host(name="<insert_name_here>", number_of_guests=0, food_requirements=[]):
    name = name.split(" ")[0]

    # number_of_guests now includes the host itself
    number_of_guests += 1

    # Rezeptvorschläge anhängen???

    if len(food_requirements) == 0:
        food_requirements_string = "Deine Gäste haben KEINE Essensbesonderheiten angegeben."
    else:
        food_requirements_string = "Deine Gäste haben folgende Essensbesonderheiten:"
        for food_requirement in food_requirements:
            food_requirements_string += f"\n\t* {food_requirement}"

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
              "Fachschaftsraum abholen." \
              "\n\n" \
              "Was du dann letztendlich machst - also was du kochen willst - kannst " \
              "du ganz allein entscheiden. Dabei kann <a href='https://www.google.de'>Google</a>, " \
              "<a href='https://www.chefkoch.de/'>Chefkoch.de</a> oder " \
              "<a href='https://www.youtube.com/user/donalskehan'>Youtube</a> eine große Hilfe sein. " \
              "Oder du kochst einfach dein Lieblingsgericht!" \
              "\n\n" \
              f"{food_requirements_string}" \
              "\n\n" \
              "Bitte hänge am Tag der Veranstaltung einen Zettel an deine Klingel mit der " \
              "Aufschrift „MSEating“, da deine Gäste deinen Namen ja (noch) nicht kennen werden! " \
              "Wir melden uns dann einen Tag vor dem Abend nochmal." \
              "\n\n" \
              "Dein MSEating - Team"
    return message


def get_message_batch_2_host(name="<insert_name_here>", guests=[]):
    name = name.split(" ")[0]

    emergency_list = ""
    for emergency_name in MSE_EMERGENCY_PHONE_NUMBERS:
        emergency_list += "\n\t* " + emergency_name + ": " + MSE_EMERGENCY_PHONE_NUMBERS[emergency_name]

    if len(guests) == 0:
        guest_contacts = "Something went wrong here... :/"
    else:
        guest_contacts = ""
        for guest in guests:
            guest_contacts += f"\t* {guest['name']}, {guest['phone_number']}, {guest['mail_address']}\n"

    message = f"Servus {name}," \
              "\n\n" \
              "das MSEating steht vor der Tür! Schon gespannt, mit wem du zusammen kochen wirst?" \
              "\n\n" \
              "Bitte denk daran, UNBEDINGT ein Schild an deiner Klingel anzubringen, worauf  " \
              "„MSEating“ steht. So können dann hoffentlich alle deine Gäste pünktlich um 18:30 " \
              "Uhr zu dir finden. Zudem solltest du schon jetzt entscheiden, was du morgen " \
              "für deine Gäste kochen willst und vielleicht sogar einkaufen / eine Einkaufsliste " \
              "schreiben. Googeln ist erlaubt ;)" \
              "\n\n" \
              "Hier die Kontaktdaten deiner Gäste, für Notfälle (Bitte behalte die Informationen " \
              "für dich, damit die Spannung nicht verloren geht!) :\n" \
              f"{guest_contacts}" \
              f"\n" \
              "Dein MSEating-Team" \
              "\n\n" \
              f"PS: Falls du Probleme haben solltest, kannst du uns gerne anrufen:" \
              f"{emergency_list}" \
              "\n\n"\
              "Wenn du das Geld noch nicht abgeholt hast, hole dies bitte so schnell wie möglich " \
              "nach! Oder willst du dir etwa die 7€ pro Teilnehmer entgehen lassen? ;) " \

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
                address = row[1].replace("\u00df", "ss") + "," + row[2].replace("\u00fc", "ue")
                address = address.replace("\"", "")

                attendees_list.append({"name": name_and_type[:-7],
                                       "number_of_guests": 0,
                                       "food_requirements": [],
                                       "address": address,
                                       "mail_address": row[4],
                                       "phone_number": row[5],
                                       "guests": []})
            else:
                if name_and_type[-7:] == "(Guest)":
                    # This row belongs to a matched guest
                    attendees_list[host_index]["guests"].append({"name": name_and_type[:-8],
                                                                 "mail_address": row[3],
                                                                 "phone_number": row[4],
                                                                 "food_requirements": row[1][11:]})
                    if row[1][11:] != "None":
                        attendees_list[host_index]["food_requirements"].append(row[1][11:])
                    attendees_list[host_index]["number_of_guests"] += 1

    return attendees_list


def send_mails_for_batch(input_file="CSV_Tables/out.csv", batch=1):
    attendees_list = get_attendees_list(input_file=input_file)
    mails = []
    for host in attendees_list:

        mail_address = host["mail_address"]

        if batch == 1:
            message = get_message_batch_1_host(name=host["name"],
                                               number_of_guests=host["number_of_guests"],
                                               food_requirements=host["food_requirements"])
            mails.append({"mail_address": mail_address, "subject": "You made it!", "message": message})
        elif batch == 2:
            message = get_message_batch_2_host(name=host["name"],
                                               guests=host["guests"])
            mails.append({"mail_address": mail_address, "subject": "Upcoming: MSEating", "message": message})
        else:
            return

        for guest in host["guests"]:

            mail_address = guest["mail_address"]

            if batch == 1:
                message = get_message_batch_1_guest(name=guest["name"])
                mails.append({"mail_address": mail_address, "subject": "You made it!", "message": message})
            elif batch == 2:
                message = get_message_batch_2_guest(name=guest["name"],
                                                    address=host["address"],
                                                    phone_number=host["phone_number"])
                mails.append({"mail_address": mail_address, "subject": "Upcoming: MSEating", "message": message})
            else:
                return

    send_mails(mails)


def send_mails(mails):

    # Set up the SMTP server
    s = smtplib.SMTP(host=SMTP_SERVER, port=SMTP_PORT)
    s.starttls()
    s.login(OUTLOOK_CREDENTIALS_USER, OUTLOOK_CREDENTIALS_PASS)

    file1 = open("mails.md", "a")

    file1.write("---\nSending Mails to: " + "\n\n")
    for mail_address in [mail['mail_address'] for mail in mails]:
        file1.write("* " + mail_address + "\n")
    file1.write("\n---\n\n")

    # for i in tqdm(range(5)):
    for i in tqdm(range(len(mails))):

        # Set up message
        msg = MIMEMultipart()
        msg['From'] = OUTLOOK_FROM_EMAIL
        msg['To'] = OUTLOOK_TO_EMAIL
        # msg['To'] = mails[i]["mail_address"]
        msg['Bcc'] = ""
        msg['Subject'] = mails[i]["subject"]
        msg.add_header('reply-to', OUTLOOK_REPLY_TO_ADDRESS)
        msg.attach(MIMEText(mails[i]["message"].replace("\n", "<br/>"), 'html'))

        file1.write(f"**Address**: {mails[i]['mail_address']}\n\n")
        file1.write(f"**Subject**: {mails[i]['subject']}\n\n")
        file1.write(f"**Content**:\n\n")
        file1.write(mails[i]["message"].replace("<br/>", "\n"))
        file1.write("\n\n---\n\n")

        # Send message
        # s.send_message(msg)

        del msg

    file1.close()


if __name__ == "__main__":
    send_mails_for_batch(batch=2)
