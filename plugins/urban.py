# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
from urllib2 import urlopen

from bs4 import BeautifulSoup

def urban(message_data, bot):
  result = urlopen('http://www.urbandictionary.com/define.php?term=' + message_data["parsed"])
  soup = BeautifulSoup(result.read())
  wordresult = soup.find('a', class_='word')
  definition = soup.find('div', class_='meaning')
  if definition:
    return wordresult.text.replace('\n','') + ': ' + definition.text.replace('\n','')
  else:
    return "Nothing found"

commands = {"urban": urban}
triggers = []

