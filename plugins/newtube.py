# Rewritten 30th May 2015 to support Youtube v3 API

from __future__ import division
# no one wants print(), go away:
#from __future__ import print_function
from __future__ import unicode_literals

import locale
import re
import time
from datetime import datetime, timedelta

# 3.0 API:
from apiclient.discovery import build

# Import ISODATE for ISO duration functions
import isodate

# Youtube API things:
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# URL bases for different search result types:
YOUTUBE_SHORT_URL = "http://youtu.be/"
YOUTUBE_PLAYLIST_URL = "http://www.youtube.com/playlist?list="
YOUTUBE_CHANNEL_URL = "http://www.youtube.com/channel/"

# Trigger regex. Detects youtube urls/IDs
# Note: Does not need capital A-Z due to re.I used on regex search in initialising code
regex = r'(?:youtube.*?(?:v=|/v/)|youtu\.be/|yooouuutuuube.*?id=)([-_a-z0-9]+)'

# Import the IRC thing, for irc.bold
from botmily import irc
from botmily import config

# Converts ISO time into a big long string with days allegedly, hours, minutes and seconds
def convertISOTime(duration):
	# Well, duration is now an ISO string in the format PT##H##M##S
	# This is a non trivial format so we use the ISODATE library for this
	# You can get it with pip install isodate
	converted_duration = isodate.parse_duration(duration)

	# Now do this same kinda weird code as before but whatever I imagine it works:
	d = datetime(1,1,1) + converted_duration
	if d.day-1 > 0:
		return '%d days %d hours %d minutes %d seconds' %(d.day-1,d.hour,d.minute,d.second)
	elif d.hour > 0:
		return '%d hours %d minutes %d seconds' %(d.hour,d.minute,d.second)
	elif d.minute > 0:
		return '%d minutes %d seconds' %(d.minute,d.second)
	else:	
		return '%d seconds' %d.second 

# Youtube API v3 Search functionality
def search(message_data, bot):
	# Create API service:
	youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=config.YOUTUBE_API_KEY)

	search_term = message_data['parsed']

	# Call the search.list method to retrieve results matching the specified
	# query term.
	search_response = youtube.search().list(
	q=search_term,
	part="id,snippet",
	maxResults=1
	).execute()

	# Technically we can differentiate between videos, channels, and playlists, but we're just going to hardcodedely report one result:
	my_result = "No results"

	# Generate the prototype for the string we will respond with:
	prototype_format = "\u0002%s\u000f - %s%s"

	# Format the result in the appropriate manner (nb we get a list because we just get a list, but it's only 1 entry long (for now...))
	for search_result in search_response.get("items", []):
		if search_result['id']['kind'] == "youtube#video":
		  my_result = (prototype_format % (search_result['snippet']['title'],YOUTUBE_SHORT_URL,search_result['id']['videoId']))
		elif search_result['id']['kind'] == "youtube#channel":
		  my_result = (prototype_format % (search_result['snippet']['title'],YOUTUBE_CHANNEL_URL,search_result['id']['channelId']))
		elif search_result['id']['kind'] == "youtube#playlist":
		  my_result = (prototype_format % (search_result['snippet']['title'],YOUTUBE_PLAYLIST_URL,search_result['id']['playlistId']))
	
	return my_result

# Youtube API v3 Video info functionality
def parse(message_data, bot):
	# Takes a message_data dictionary as a param
	# Get the regex match entry from the dictionry, and select result 1 from it. This is all done in the bot script somewhere.
 	video_id = message_data['re'].group(1)

	# Create API service:
	youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=config.YOUTUBE_API_KEY)

	# Call the videos.list method to retrieve results matching the specified
	# query term.
	video_responces = youtube.videos().list(
	id=video_id,
	part="id,snippet,contentDetails,statistics" # We call all these things to uh, well I don't know why we do ID really, but we do it to get all the info we need
	).execute()
	# snippet has most of the title/uploader/date info
	# contentDetails has the duration
	# statistics has the likes/views

	my_result = None

	for video_responce in video_responces.get("items", []):
		if video_responce['kind'] == "youtube#video":
			my_result = irc.bold(unicode(video_responce['snippet']['title'])) + " - length "
			my_result += irc.bold(convertISOTime(video_responce['contentDetails']['duration']))

			# Generate score out of 5 I guess?
			# Get how many likes/dislikes the video has
			likes = int(video_responce['statistics']['likeCount'])
			dislikes = int(video_responce['statistics']['dislikeCount'])
			# Work out the total
			totals = likes + dislikes
			# If non zero, add the score
			if totals > 0:
				score = 5 * (float(likes) / float(totals))
				my_result += " - rated " + irc.bold(locale.format("%.2f", score)) + "/5.0 (" + locale.format("%d",totals) + ")"

			# Do something entirely dissimilar but the same kinda for the views. Which is to say: add the views
			views = video_responce['statistics']['viewCount']
			if views:
				my_result += " - " + irc.bold(views) + " views"

			# Add the remaining user and upload time fields:
			my_result += " - " + irc.bold(unicode(video_responce['snippet']['channelTitle'])) + " on "
			my_result += irc.bold(time.strftime("%Y.%m.%d", time.strptime(video_responce['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%S.000Z")))

 	return my_result

# Register with the bot:
commands = {"youtube": search, "y": search, "yt": search}
triggers = [(regex, parse)]
