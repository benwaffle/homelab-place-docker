import math
import sys
import time

import requests
from PIL import Image
from requests.adapters import HTTPAdapter

img = Image.open(sys.argv[1])
origin = (int(sys.argv[2]), int(sys.argv[3]))
username = sys.argv[4]
password = sys.argv[5]


def find_palette(point):
    rgb_code_dictionary = {
        (255, 255, 255): 0,
        (228, 228, 228): 1,
        (136, 136, 136): 2,
        (34, 34, 34): 3,
        (255, 167, 209): 4,
        (229, 0, 0): 5,
        (229, 149, 0): 6,
        (160, 106, 66): 7,
        (229, 217, 0): 8,
        (148, 224, 68): 9,
        (2, 190, 1): 10,
        (0, 211, 211): 11,
        (0, 131, 199): 12,
        (0, 0, 234): 13,
        (207, 110, 228): 14,
        (130, 0, 128): 15
    }

    def distance(c1, c2):
        (r1, g1, b1) = c1
        (r2, g2, b2) = c2
        return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

    colors = list(rgb_code_dictionary.keys())
    closest_colors = sorted(colors, key=lambda color: distance(color, point))
    closest_color = closest_colors[0]
    code = rgb_code_dictionary[closest_color]
    return code


s = requests.Session()
s.mount('https://www.reddit.com', HTTPAdapter(max_retries=5))
s.headers["User-Agent"] = "PlacePlacer"
r = s.post("https://www.reddit.com/api/login/{}".format(username),
           data={"user": username, "passwd": password, "api_type": "json"})
s.headers['x-modhash'] = r.json()["json"]["data"]["modhash"]


def place_pixel(ax, ay, new_color):
    print("Probing absolute pixel {},{}".format(ax, ay))

    while True:
        r = s.get("http://reddit.com/api/place/pixel.json?x={}&y={}".format(ax, ay), timeout=5)
        if r.status_code == 200:
            data = r.json()
            break
        else:
            print("ERROR: ", r, r.text)
        time.sleep(5)

    old_color = data["color"] if "color" in data else 0
    if old_color == new_color:
        print("Color #{} at {},{} already exists (placed by {}), skipping".format(new_color, ax, ay, data[
            "user_name"] if "user_name" in data else "<nobody>"))
    else:
        print("Placing color #{} at {},{}".format(new_color, ax, ay))
        r = s.post("https://www.reddit.com/api/place/draw.json",
                   data={"x": str(ax), "y": str(ay), "color": str(new_color)})

        secs = float(r.json()["wait_seconds"])
        if "error" not in r.json():
            print("Placed color - waiting {} seconds".format(secs))
        else:
            print("Cooldown already active - waiting {} seconds".format(int(secs)))
        time.sleep(secs + 2)

        if "error" in r.json():
            place_pixel(ax, ay, new_color)


for y in range(img.height):
    for x in range(img.width):
        pixel = img.getpixel((x, y))

        if pixel[3] > 0:
            pal = find_palette((pixel[0], pixel[1], pixel[2]))

            ax = x + origin[0]
            ay = y + origin[1]

            place_pixel(ax, ay, pal)
