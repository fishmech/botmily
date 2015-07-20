# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
from urllib2 import urlopen

from bs4 import BeautifulSoup

def etymology(message_data, bot):
	result = urlopen('http://www.etymonline.com/index.php?term=' + message_data["parsed"])
	reply = ''
	soup = BeautifulSoup(result.read()) #BeautifulStoneSoup(result, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
	if soup.dl is None:
		reply = 'Not found'
	else:
		reply = "".join(soup.dl.findAll(text=True)).replace("\n", " ")
	if reply == 'Not found':
		return reply
	else:
		return reply[:300]+'... http://www.etymonline.com/index.php?term=' + message_data["parsed"]

commands = {"etymology": etymology}
triggers = []

