# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
from urllib2 import urlopen

from bs4 import BeautifulSoup

from botmily import irc

def steam(message_data, bot):
	result = urlopen('http://alabasterslim.com/worth.php?account=' + message_data["parsed"])
	soup = BeautifulSoup(result.read())
	error = soup.find('div',id='centredetail')
	if error is not None:
		output = 'Nothing found'
	else:
		data = soup.find_all('fieldset')
		resultfield = data[1].text.encode('ascii','ignore')
		output = message_data["parsed"].encode('utf-8') + ' owns' + resultfield[resultfield.find('You own')+7:resultfield.find(' - What does this')].encode('utf-8') + ' - http://alabasterslim.com/worth.php?account=' + message_data["parsed"].encode('utf-8')
	return output

commands = {"sc": steam, "steamcalc": steam}
triggers = []

