# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
from urllib import quote_plus
import urllib2
from xml.etree import ElementTree

from botmily.db import db

def weather(message_data, bot):
    db.execute("create table if not exists weather(nick primary key, loc)")
    loc = message_data["parsed"]
    if loc == "":
        row = db.execute("select loc from weather where nick=:nick", {"nick": message_data["nick"]}).fetchone()
        if not row:
            return 'Type in a location ¬_¬'
        loc = row[0]
    else:
        db.execute("insert or replace into weather(nick, loc) values (:nick, :loc)", {"nick": message_data["nick"], "loc": loc})
        db.commit()
    try:
        result = urllib2.urlopen('http://api.wunderground.com/api/91ef6bb1dc828118/conditions/q/' + quote_plus(loc) + '.xml')
    except urllib2.URLError:
        return "Error getting weather data"
    try:
        weather = ElementTree.fromstring(result.read())
    except ElementTree.ParseError:
        return "Error getting weather data"
    current_observation = weather.find('current_observation')
    results = weather.find('results')
    if current_observation is not None:
        display_location = current_observation.find('display_location')
        string = display_location.find('full').text + ': '
        string += current_observation.find('weather').text + ', '
        string += current_observation.find('temperature_string').text + ', '
        string += current_observation.find('relative_humidity').text + ', Wind is blowing '
        string += current_observation.find('wind_string').text.replace('F','f', 1) + '.'
    elif results is not None:
        string = "Found the following cities/locations, please specify: "
        for r in results:
            string += "[ " + r.find('name').text + ', ' + r.find('city').text + ', '
            state = r.find('state')
            if state.text is not None:
                string += state.text + ', '
            string += r.find('country_name').text + "(" + r.find('country').text + ") ] "
    else:
        string = "City/location not found"
    return string

commands = {"weather": weather}
triggers = []

if __name__ == '__main__':
    import sys
    if (len(sys.argv) < 2):
        print("Please provide search-argument")
        sys.exit(1)
    print(weather({"parsed" : sys.argv[1]},None))
