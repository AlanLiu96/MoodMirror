# {
#     'maroon': [0, 100, 50.2],
#     'red': [0, 100, 100],
#     'orange': [39, 100, 100],
#     'yellow': [60, 100, 100],
#     'olive': [60, 100, 50.2],
#     'purple': [300, 100, 50.2],
#     'fuchsia': [300, 100, 100],
#     'white': [0, 0, 100],
#     'lime': [120, 100, 100],
#     'green':
#     'navy':
#     'blue':
#     'aqua':
#     'teal':
#     'black':
#     'silver':
#     'gray':
# }

import webcolors
import colorsys

def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name

def colorName(r, g, b):
    actual_name, closest_name = get_colour_name((r, g, b))
    return closest_name

def triad(r, g, b):
    color = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    newColor = ((color[0] + 0.3333) % 1, color[1] / 1.1, 1 - color[2])
    return colorsys.hsv_to_rgb(newColor[0], newColor[1], newColor[2])

def colorRec(r, g, b):
    color = triad(r, g, b)
    return colorName(color[0] * 255, color[1] * 255, color[2] * 255)