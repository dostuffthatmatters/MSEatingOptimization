from PIL import Image, ImageDraw, ImageFont

from Optimization.attendee import Host, Guest
from Helpers.custom_printing import CustomPrinting


def export_image():
    CustomPrinting.print_pink(f"#6 Generating Image")

    """

    min_lat = 1000
    min_lng = 1000

    max_lat = 0
    max_lng = 0

    for attendee in Host.instances + Guest.instances:
        if attendee.lat > max_lat:
            max_lat = attendee.lat
        if attendee.lat < min_lat:
            min_lat = attendee.lat

        if attendee.lng > max_lng:
            max_lng = attendee.lng
        if attendee.lng < min_lng:
            min_lng = attendee.lng

    lat_adjustment = (max_lat - min_lat) * 0.1
    lng_adjustment = (max_lng - min_lng) * 0.1

    min_lat -= lat_adjustment
    max_lat += lat_adjustment

    min_lng -= lng_adjustment
    max_lng += lng_adjustment

    """

    img = Image.open("Source/munich.png")

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Source/Courier_New_Bold.ttf", 20)

    min_lat = 48.057483
    max_lat = 48.253319

    min_lng = 11.352409
    max_lng = 11.730366

    width = 3335
    height = 2603
    linewidth = 6

    # img = Image.new(mode="RGB", size=(1000, 1000), color=(220, 220, 220))

    # draw.polygon((0, 0, 0, 1280, 1280, 1280, 1280, 0), fill=(255, 255, 255, 0.5))

    green_dots_to_be_drawn = []
    red_dots_to_be_drawn = []
    blue_dots_to_be_drawn = []

    host_locations = {}
    dot_locations = {}

    for host in Host.instances:
        x_host = round(width * (host.lng - min_lng)/(max_lng - min_lng))
        y_host = height - round(height * (host.lat - min_lat)/(max_lat - min_lat))

        if x_host not in host_locations:
            host_locations[x_host] = {y_host: f"{len(host.guests)}"}
        elif y_host not in host_locations[x_host]:
            host_locations[x_host][y_host] = f"{len(host.guests)}"
        else:
            host_locations[x_host][y_host] += f"/{len(host.guests)}"

        for guest in host.guests:
            x_guest = round(width * (guest.lng - min_lng) / (max_lng - min_lng))
            y_guest = height - round(height * (guest.lat - min_lat) / (max_lat - min_lat))
            draw.line((x_host, y_host, x_guest, y_guest), fill=(50, 50, 50), width=linewidth)

            if x_guest not in dot_locations:
                dot_locations[x_guest] = {y_guest: 1}
            elif y_guest not in dot_locations[x_guest]:
                dot_locations[x_guest][y_guest] = 1
            else:
                dot_locations[x_guest][y_guest] += 1

            green_dots_to_be_drawn.append([x_guest, y_guest])

        if x_host not in dot_locations:
            dot_locations[x_host] = {y_host: 1}
        elif y_host not in dot_locations[x_host]:
            dot_locations[x_host][y_host] = 1
        else:
            dot_locations[x_host][y_host] += 1

        blue_dots_to_be_drawn.append([x_host, y_host])

    for guest in Guest.instances:
        if guest.host is None:
            x = round(width * (guest.lng - min_lng) / (max_lng - min_lng))
            y = height - round(height * (guest.lat - min_lat) / (max_lat - min_lat))

            if x not in dot_locations:
                dot_locations[x] = {y: 1}
            elif y not in dot_locations[x]:
                dot_locations[x][y] = 1
            else:
                dot_locations[x][y] += 1
            red_dots_to_be_drawn.append([x, y])

    for dot in red_dots_to_be_drawn:
        x = dot[0]
        y = dot[1]

        markersize = 24 + (12 * (dot_locations[x][y] - 1))
        color = (175, 0, 0) if dot_locations[x][y] % 2 == 0 else (255, 0, 0)
        dot_locations[x][y] -= 1

        draw.ellipse((x - markersize / 2, y - markersize / 2, x + markersize / 2, y + markersize / 2), fill=color)

    for dot in green_dots_to_be_drawn:
        x = dot[0]
        y = dot[1]

        markersize = 24 + (12 * (dot_locations[x][y] - 1))
        color = (0, 130, 0) if dot_locations[x][y] % 2 == 0 else (0, 200, 0)
        dot_locations[x][y] -= 1

        draw.ellipse((x - markersize / 2, y - markersize / 2, x + markersize / 2, y + markersize / 2), fill=color)

    for dot in blue_dots_to_be_drawn:
        x = dot[0]
        y = dot[1]

        markersize = 24 + (12 * (dot_locations[x][y] - 1))
        color = (0, 0, 175) if dot_locations[x][y] % 2 == 0 else (0, 0, 255)
        dot_locations[x][y] -= 1

        draw.ellipse((x - markersize / 2, y - markersize / 2, x + markersize / 2, y + markersize / 2), fill=color)

        if dot_locations[x][y] == 0:
            text = host_locations[x][y]
            draw.text((x-(len(text)*6), y-10), text, font=font, fill=(255, 100, 100))

    img.save("Source/out.png")
    CustomPrinting.print_pink(f"#6 Generating Image: Done", new_lines=3)

    img.show()
