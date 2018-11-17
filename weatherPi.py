#!/usr/bin/env python

# imports
import json                 # weather data
import time                 # time data
import urllib               # fixing urls
import includes.epd2in13b   # e ink library
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


# Get the weather data for the given location
location_string = "{city}, {countrycode}".format(city=CITY, countrycode=COUNTRYCODE)
weather = get_weather(location_string)


# This maps the weather codes from the Yahoo weather API
# to the appropriate weather icons
icon_map = {
    "snow": [5, 6, 7, 8, 10, 13, 14, 15, 16, 17, 18, 41, 42, 43, 46],
    "rain": [9, 11, 12],
    "cloud": [19, 20, 21, 22, 25, 26, 27, 28, 29, 30, 44],
    "sun": [32, 33, 34, 36],
    "storm": [0, 1, 2, 3, 4, 37, 38, 39, 45, 47],
    "wind": [23, 24]
}