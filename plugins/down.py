from __future__ import division
#from __future__ import print_function
from __future__ import unicode_literals

import urllib2

# Checks if a website is down
def down(message_data, bot):
    '''.down <url> -- checks to see if the site is down'''
    webaddress = message_data['parsed'].strip()
    if 'http://' not in webaddress:
        webaddress = 'http://' + webaddress

    try:
        result = urllib2.urlopen(webaddress)
        return webaddress + " seems to be up."
    except urllib2.URLError:
        return webaddress + " seems to be down."

commands = {"down": down}
triggers = []