#!/usr/bin/env python

# imports
import json                 # weather data
import time                 # time data
import urllib               # fixing urls
from includes import epd2in13b   # e ink library
import Image                # Image manipulation
import ImageFont            # Text Writing
import ImageDraw            # Image drawing

try:
    import requests         # needed for getting data
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")


# statc vars
COLORED = 1
UNCOLORED = 0
CITY = "Minneapolis"
COUNTRYCODE = "US"

# Weather code taken from inky-phat example code
# Python 2 vs 3 breaking changes
def encode(qs):
    val = ""
    try:
        val = urllib.urlencode(qs).replace("+", "%20")
    except AttributeError:
        val = urllib.parse.urlencode(qs).replace("+", "%20")
    return val

# Query the Yahoo weather API to get current weather data
def get_weather(address):
    base = "https://query.yahooapis.com/v1/public/yql?"
    query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text=\"{}\")".format(address)
    qs = {"q": query, "format": "json", "env": "store://datatables.org/alltableswithkeys"}

    uri = base + encode(qs)

    res = requests.get(uri)
    if res.status_code == 200:
        json_data = json.loads(res.text)
        return json_data

    return {}

##############################################################################
##############################################################################
# Start of main program 
##############################################################################
##############################################################################

# startup display
disp=epd2in13b.EPD()
disp.init()

# image frames to be drawn
frame_black = [0xFF] * (disp.width * disp.height / 8)
frame_yellow = [0xFF] * (disp.width * disp.height / 8)

# fonts to be used
fontBold = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 35)
font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 35)

# Get the weather data for the given location
location_string = "{city}, {countrycode}".format(city=CITY, countrycode=COUNTRYCODE)
weather = get_weather(location_string)

# This maps the weather codes from the Yahoo weather API
# to the appropriate weather icons
icon_map = {
    "snow": [5, 6, 7, 13, 14, 15, 16, 17, 18, 41, 42, 43, 46],
    "rain": [8, 9, 10, 11, 12, 35, 40],
    "cloud": [19, 20, 21, 22, 25, 26, 27, 28, 44],
    "pcloud": [30, 44],
    "pcloudnight": [29],
    "night": [31,33],
    "sun": [32, 34, 36],
    "storm": [0, 1, 2, 3, 4, 37, 38, 39, 45, 47],
    "wind": [23, 24]
}

# Placeholder variables
highT = 0
lowT =0
weather_icon = None

# Pull out the appropriate values from the weather data
if "channel" in weather["query"]["results"]:
    results = weather["query"]["results"]["channel"]
    highT = int(results["item"]["forecast"][0]["high"])
    lowT = int(results["item"]["forecast"][0]["low"])
    code = int(results["item"]["forecast"][0]["code"])

    for icon in icon_map:
        if code in icon_map[icon]:
            weather_icon = icon
            break
else:
    print("Warning, no weather information found!")

# get date info
weekday=time.strftime('%a')
month=time.strftime('%b')
date=time.strftime('%d')


## draw images first
# black part
frame_black= disp.get_frame_buffer(Image.open('images/black/cloudy.bmp'))

# yellow part
#frame_yellow= disp.get_frame_buffer(Image.open('images/black/cloudy.bmp'))

## draw Text
disp.set_rotate(1)
disp.draw_string_at(frame_black, 15, 5, weekday, fontBold, COLORED)
disp.draw_string_at(frame_black, 60, 5, month, font, COLORED)
disp.draw_string_at(frame_black, 130, 5, date, fontBold, COLORED)

# display it 
disp.display_frame(frame_black,frame_yellow)
