

def get_attendees_list(input_file="out.csv"):
    attendees_list = []
    return attendees_list


def send_mails(input_file="out.csv"):
    attendees_list = get_attendees_list(input_file=input_file)
    attendees_list += [1]


if __name__ == "__main__":
    send_mails()
