from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ConfigParser import ConfigParser

name = ''
server = ''
channels = []
password = ''
timeout = 300
tumblr_blog = ''
tumblr_user = ''
tumblr_password = ''
tumblr_title = ''
tumblr_tumbling = False
wolframalpha_api_key = ''
lastfm_api_key = ''

def getConfig():
    global name
    global server
    global channels
    global password
    global timeout
    global wolframalpha_api_key
    global lastfm_api_key
    global oauth_token
    global oauth_secret
    global consumer_key
    global consumer_secret
    global YOUTUBE_API_KEY
    config = ConfigParser()
    config.read('config.ini')
    name = config.get('main', 'name')
    server = config.get('main', 'server')
    channels = config.get('main', 'channels').split(" ")
    password = config.get('main', 'password')
    try:
        timeout = int(config.get('main', 'timeout'))
    except:
        print("Could not convert timeout value to integer! Defaulting to 300!")
        timeout = 300
    wolframalpha_api_key = config.get('wolframalpha', 'api_key')
    lastfm_api_key = config.get('lastfm', 'api_key')
    oauth_token = config.get('twitter', 'oauth_token')
    oauth_secret = config.get('twitter', 'oauth_secret')
    consumer_key = config.get('twitter', 'consumer_key')
    consumer_secret = config.get('twitter', 'consumer_secret')
    YOUTUBE_API_KEY = config.get('youtube', 'api_key')
    print("I will use the name: " + name)
    print("I will connect to the server: " + server)
    print("I will connect to the channels: " + ", ".join(channels))
