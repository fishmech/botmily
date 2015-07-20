# -*- coding: utf-8 -*-
#copied from fixed version of .urban


from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from urllib2 import urlopen

from ratebeer import RateBeer

def beer(message_data, bot):
	rb = RateBeer()
	results = rb.search(message_data["parsed"])
	highest_ratings = -1 #get at least 1
	if results['beers']:
		for beer in results['beers']:
			if beer['num_ratings'] > highest_ratings: #pull highest rated beer from result set
				topbeer = beer
				topdetails = rb.beer(beer['url'])
				highest_ratings = beer['num_ratings']
		if 'overall_rating' in topbeer: #overall_rating doesn't always exist http://www.ratebeer.com/ratingsqa.asp
			reply =  topbeer['name'].encode('utf-8') + ': Rating ' + str(topbeer['overall_rating']) + ', http://www.ratebeer.com'+ topbeer['url'].encode('utf-8') + ' '
		else:
			reply = topbeer['name'].encode('utf-8') + ': http://www.ratebeer.com'+ topbeer['url'].encode('utf-8') + ' (' + str(topbeer['num_ratings']) +' ratings) '
		
		reply += topdetails['style'].encode('utf-8') + ', ' + str(topdetails['abv']) + "% ABV, " + str(topdetails['calories']) + ' calories from alcohol, brewed by ' + topdetails['brewery'].encode('utf-8')
	else:
		reply = 'Not Found'
	return reply.encode('utf-8')
	
commands = {"beer": beer}
triggers = []

