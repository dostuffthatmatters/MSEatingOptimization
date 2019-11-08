from PIL import Image, ImageDraw, ImageFont

from Optimization.attendee import Host, Guest
from Helpers.custom_printing import CustomPrinting
from Helpers.custom_logger import CustomLogger

from time import time
import logging

logging.getLogger('pillow').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.getLogger('pil').setLevel(logging.WARNING)


def draw_image(source="Source/munich.png",
               destination="Source/munich_out.png",
               min_lat=48.057483,
               max_lat=48.253319,
               min_lng=11.352409,
               max_lng=11.730366,
               size_multiplier=1):
    """
        This function generates and saves and images based on
        the current Host/Guest configuration.
    """

    # Static background image of munich on which is painted on
    img = Image.open(source)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Source/Courier_New_Bold.ttf", round(20 * size_multiplier))

    """
    # Dimensions of the images
    width = 3335
    height = 2603
    """

    # Dimensions of the elements to be drawn
    width, height = img.size
    line_width = round(6 * size_multiplier)
    circle_size = round(24 * size_multiplier)
    ring_steps = round(12 * size_multiplier)

    # Determining all dots to be drawn (x, y)-image-coordinates
    green_dots_to_be_drawn = []
    red_dots_to_be_drawn = []
    blue_dots_to_be_drawn = []

    # Storing the number of dots at each (x, y)-image-coordinate,
    # so that multiple points at one spot can be printed as concentric
    # circles with increasing size
    dot_locations = {}

    # Storing the number of guests for each host in a string
    # (One host: "4", Two hosts: "4/5", ...)
    host_locations = {}

    # Determine all host dots (blue) and draw all lines between
    # hosts and guests
    for host in Host.instances:
        x_host = round(width * (host.lng - min_lng) / (max_lng - min_lng))
        y_host = height - round(height * (host.lat - min_lat) / (max_lat - min_lat))

        # Updating the number of guests for this host_hub as a string
        if x_host not in host_locations:
            host_locations[x_host] = {y_host: f"{len(host.guests)}"}
        elif y_host not in host_locations[x_host]:
            host_locations[x_host][y_host] = f"{len(host.guests)}"
        else:
            host_locations[x_host][y_host] += f"/{len(host.guests)}"

        # Determine all matched-guest dots (green) to be drawn and draw lines between each guest and its host
        for guest in host.guests:
            x_guest = round(width * (guest.lng - min_lng) / (max_lng - min_lng))
            y_guest = height - round(height * (guest.lat - min_lat) / (max_lat - min_lat))
            draw.line((x_host, y_host, x_guest, y_guest), fill=(50, 50, 50), width=line_width)

            # Updating the number of dots at this (x, y)-image-coordinate
            if x_guest not in dot_locations:
                dot_locations[x_guest] = {y_guest: 1}
            elif y_guest not in dot_locations[x_guest]:
                dot_locations[x_guest][y_guest] = 1
            else:
                dot_locations[x_guest][y_guest] += 1

            green_dots_to_be_drawn.append([x_guest, y_guest])

        # Updating the number of dots at this (x, y)-image-coordinate
        if x_host not in dot_locations:
            dot_locations[x_host] = {y_host: 1}
        elif y_host not in dot_locations[x_host]:
            dot_locations[x_host][y_host] = 1
        else:
            dot_locations[x_host][y_host] += 1

        blue_dots_to_be_drawn.append([x_host, y_host])

    # Determine all not-matched-guest dots (red) to be drawn
    for guest in filter(lambda guest: guest.host is None, Guest.instances):
        x = round(width * (guest.lng - min_lng) / (max_lng - min_lng))
        y = height - round(height * (guest.lat - min_lat) / (max_lat - min_lat))

        # Updating the number of dots at this (x, y)-image-coordinate
        if x not in dot_locations:
            dot_locations[x] = {y: 1}
        elif y not in dot_locations[x]:
            dot_locations[x][y] = 1
        else:
            dot_locations[x][y] += 1
        red_dots_to_be_drawn.append([x, y])

    # Draw all red dots first (most outer circles)
    for dot in red_dots_to_be_drawn:
        x = dot[0]
        y = dot[1]

        markersize = circle_size + (ring_steps * (dot_locations[x][y] - 1))
        color = (175, 0, 0) if dot_locations[x][y] % 2 == 0 else (255, 0, 0)
        dot_locations[x][y] -= 1

        draw.ellipse((x - markersize / 2, y - markersize / 2, x + markersize / 2, y + markersize / 2), fill=color)

    # Draw all green dots second (inside of red circles but outside of blue circles)
    for dot in green_dots_to_be_drawn:
        x = dot[0]
        y = dot[1]

        markersize = circle_size + (ring_steps * (dot_locations[x][y] - 1))
        color = (0, 130, 0) if dot_locations[x][y] % 2 == 0 else (0, 200, 0)
        dot_locations[x][y] -= 1

        draw.ellipse((x - markersize / 2, y - markersize / 2, x + markersize / 2, y + markersize / 2), fill=color)

    # Draw all blue dots last (most inner circles)
    for dot in blue_dots_to_be_drawn:
        x = dot[0]
        y = dot[1]

        markersize = circle_size + (ring_steps * (dot_locations[x][y] - 1))
        color = (0, 0, 175) if dot_locations[x][y] % 2 == 0 else (0, 0, 255)
        dot_locations[x][y] -= 1

        draw.ellipse((x - markersize / 2, y - markersize / 2, x + markersize / 2, y + markersize / 2), fill=color)

        # Draw the number of guests at each HostHub
        if dot_locations[x][y] == 0:
            text = host_locations[x][y]
            draw.text((x - (len(text) * 6), y - 10), text, font=font, fill=(255, 100, 100))

    img.save(destination)



# noinspection PyShadowingNames
def export_image():
    CustomLogger.info(f"#5 Generating Images ...")
    time1 = time()

    # I downloaded a static image and evaluated the boundaries myself
    source = "Source/munich.png"
    destination = "Source/munich_out.png"
    min_lat = 48.057483
    max_lat = 48.253319
    min_lng = 11.352409
    max_lng = 11.730366
    size_multiplier = 1

    draw_image(source=source,
               destination=destination,
               min_lat=min_lat,
               max_lat=max_lat,
               min_lng=min_lng,
               max_lng=max_lng,
               size_multiplier=size_multiplier)

    CustomLogger.info(f"#5 Generating Images: Done ({round(time() - time1, 6)} seconds).")
