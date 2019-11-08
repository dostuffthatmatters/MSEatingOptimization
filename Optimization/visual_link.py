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
    medium_font = ImageFont.truetype("Source/Courier_New_Bold.ttf", 30)
    big_font = ImageFont.truetype("Source/Courier_New_Bold.ttf", round(60 * size_multiplier))

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

    img_colors_legend_01 = (0, 215, 0)
    img_colors_legend_12 = (155, 232, 0)
    img_colors_legend_23 = (255, 213, 0)
    img_colors_legend_34 = (255, 149, 0)
    img_colors_legend_45 = (255, 106, 0)
    img_colors_legend_5p = (255, 0, 0)

    line_colors = [img_colors_legend_01,
                   img_colors_legend_12,
                   img_colors_legend_23,
                   img_colors_legend_34,
                   img_colors_legend_45,
                   img_colors_legend_5p]

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
            distance_category_index = round((guest.distance_to_hub / 1000.0) - 0.499999)
            distance_category_index = 5 if distance_category_index > 5 else distance_category_index
            draw.line((x_host, y_host, x_guest, y_guest), fill=line_colors[distance_category_index], width=line_width)

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
            draw.text((x - (len(text) * 6 * size_multiplier), y - (10 * size_multiplier)), text, font=font, fill=(255, 100, 100))

    # Counting the number of times each distance category exists
    # Categories: 0-1km, 1-2km, 2-3km, 3-4km, 4-5km, 5+km
    distance_categories_count = [0, 0, 0, 0, 0, 0]

    matched_guests = list(filter(lambda x: x.assigned_to_hub, Guest.instances))
    average_travel_distance = 0
    for guest in matched_guests:
        average_travel_distance += guest.distance_to_hub
        distance_category_index = round((guest.distance_to_hub / 1000.0) - 0.499999)
        distance_category_index = 5 if distance_category_index > 5 else distance_category_index
        distance_categories_count[distance_category_index] += 1

    average_travel_distance /= len(matched_guests)


    draw.text((20, 20), f"Average Travel Distance = {round(average_travel_distance,2)} meters", font=big_font, fill=(200, 0, 0))

    img_coords_rect_box = (20, height-20, 700, height-(6*80)-20-10)
    img_coords_legend_rect_01 = (35, height-35, 95, height-95)
    img_coords_legend_rect_12 = (35, height-115, 95, height-175)
    img_coords_legend_rect_23 = (35, height-195, 95, height-255)
    img_coords_legend_rect_34 = (35, height-275, 95, height-335)
    img_coords_legend_rect_45 = (35, height-355, 95, height-415)
    img_coords_legend_rect_5p = (35, height-435, 95, height-495)

    img_coords_legend_text_01 = (110, height - 80)
    img_coords_legend_text_12 = (110, height - 160)
    img_coords_legend_text_23 = (110, height - 240)
    img_coords_legend_text_34 = (110, height - 320)
    img_coords_legend_text_45 = (110, height - 400)
    img_coords_legend_text_5p = (110, height - 480)

    draw.rectangle(img_coords_rect_box, fill=(255, 255, 255))
    draw.rectangle(img_coords_legend_rect_01, fill=img_colors_legend_01)
    draw.rectangle(img_coords_legend_rect_12, fill=img_colors_legend_12)
    draw.rectangle(img_coords_legend_rect_23, fill=img_colors_legend_23)
    draw.rectangle(img_coords_legend_rect_34, fill=img_colors_legend_34)
    draw.rectangle(img_coords_legend_rect_45, fill=img_colors_legend_45)
    draw.rectangle(img_coords_legend_rect_5p, fill=img_colors_legend_5p)

    draw.text(img_coords_legend_text_01, f"      < 1.000 m -> {distance_categories_count[0]} Guests", font=medium_font, fill=img_colors_legend_01)
    draw.text(img_coords_legend_text_12, f"1.000 - 2.000 m -> {distance_categories_count[1]} Guests", font=medium_font, fill=img_colors_legend_12)
    draw.text(img_coords_legend_text_23, f"2.000 - 3.000 m -> {distance_categories_count[2]} Guests", font=medium_font, fill=img_colors_legend_23)
    draw.text(img_coords_legend_text_34, f"3.000 - 4.000 m -> {distance_categories_count[3]} Guests", font=medium_font, fill=img_colors_legend_34)
    draw.text(img_coords_legend_text_45, f"4.000 - 5.000 m -> {distance_categories_count[4]} Guests", font=medium_font, fill=img_colors_legend_45)
    draw.text(img_coords_legend_text_5p, f"5.000 <         -> {distance_categories_count[5]} Guests", font=medium_font, fill=img_colors_legend_5p)

    draw.text((20, 20), f"Average Travel Distance = {round(average_travel_distance,2)} meters", font=big_font, fill=(200, 0, 0))

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

    # I downloaded a static image and evaluated the boundaries myself
    source = "Source/munich_large.png"
    destination = "Source/munich_large_out.png"
    min_lat = 48.057483
    max_lat = 48.253319
    min_lng = 11.352409
    max_lng = 11.730366
    size_multiplier = 1.5

    # """
    draw_image(source=source,
               destination=destination,
               min_lat=min_lat,
               max_lat=max_lat,
               min_lng=min_lng,
               max_lng=max_lng,
               size_multiplier=size_multiplier)
    # """

    CustomLogger.info(f"#5 Generating Images: Done ({round(time() - time1, 6)} seconds).")
