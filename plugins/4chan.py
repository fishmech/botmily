# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import random
import re
from urllib2 import urlopen

from bs4 import BeautifulSoup

import imgur
import makeMacro

def fourchan(message_data, bot):
    board = ''

    # Commands that should be treated as gross:
    pm_commands = ["slurm","j","dudes","ecchi","hentai","dick"]

    # This could have been a dict btw lol
    if message_data['command'] == "anime":
        board = "/a/"
    elif message_data['command'] == "dick":
        board = "/d/"
    elif message_data['command'] == "dudes":
        board = "/hm/"
    elif message_data['command'] == "j":
        board = "/s/"
    elif message_data['command'] == "slurm":
        board = "/lgbt/"
    elif message_data['command'] == "technology":
        board = "/g/"
    elif message_data['command'] == "videogame":
        board = "/v/"
    elif message_data['command'] == "animals":
        board = "/an/"
    elif message_data['command'] == "hentai":
        board = "/h/"
    elif message_data['command'] == "ecchi":
        board = "/e/"
    elif message_data['command'] == "pokemon":
        board = "/vp/"

    result = urlopen('http://boards.4chan.org' + board)
    soup = BeautifulSoup(result.read()) #BeautifulStoneSoup(result, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    images = soup.find_all('a',class_='fileThumb') #soup.findAll('a', attrs={'class': 'fileThumb'})
    url = 'http:' + random.choice(images)['href']
    if message_data['parsed'] != "":
        makeMacro.makeMacro(url, message_data['parsed'], "temp.jpg")
        url = imgur.postToImgur(str("temp.jpg"))

    if message_data['command'] in pm_commands:
        return {"output":url, "channel": bot.nickname}
    else:
        return url

commands = {"technology": fourchan, "slurm":  fourchan, "j": fourchan, "dudes": fourchan, "animals": fourchan, "pokemon": fourchan, "ecchi": fourchan, "videogame": fourchan, "hentai": fourchan, "anime": fourchan, "dick": fourchan}
triggers = []

