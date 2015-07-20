# -*- coding: utf-8 -*-
#copied from fixed version of .urban


from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

from urllib2 import urlopen

from bs4 import BeautifulSoup
from util import urlnorm, http
from botmily import config


# regex for detecting websites
regex = r"(?i)forums\.somethingawful\.com/\S+threadid=(\d+)"
showthread = "http://forums.somethingawful.com/showthread.php?noseen=1"

def somethingawful(message_data, bot):
	if message_data["parsed"][:5] == "post ":
		try:
			n = int(message_data["parsed"][5:])
			output = 'http://forums.somethingawful.com/showthread.php?action=showpost&postid=' + message_data["parsed"][5:]
		except ValueError:
			output = 'Invalid input'
	return output


def login(user, password):
	http.jar.clear_expired_cookies()
	if any(cookie.domain == 'forums.somethingawful.com' and	cookie.name == 'bbuserid' for cookie in http.jar):
		if any(cookie.domain == 'forums.somethingawful.com' and	cookie.name == 'bbpassword' for cookie in http.jar):
			return
		assert("malformed cookie jar")
	http.get("http://forums.somethingawful.com/account.php", cookies=True, post_data="action=login&username=%s&password=%s" % (user, password))


def urltranslatesa(message_data, bot):
	#get url and normalize
	url = urlnorm.normalize(message_data['re'].group().encode('utf-8'))
	if config.sa_user is None or config.sa_password is None:
		return
	login(config.sa_user, config.sa_password)
	thread = http.get_html(showthread, threadid=message_data['re'].group(1), perpage='1', cookies=True)
	breadcrumbs = thread.xpath('//div[@class="breadcrumbs"]//a/text()')
	if not breadcrumbs:
		return
	thread_title = breadcrumbs[-1]
	forum_title = breadcrumbs[-2]
	poster = thread.xpath('//dt[contains(@class, author)]//text()')[0]
	# 1 post per page => n_pages = n_posts
	num_posts = thread.xpath('//a[@title="Last page"]/@href')
	print(num_posts)
	if not num_posts:
		num_posts = 1
	else:
		num_posts = int(num_posts[0].rsplit('=', 1)[1])
	return '\x02%s\x02 > \x02%s\x02 by \x02%s\x02, %s post%s' % (forum_title, thread_title, poster, num_posts,'s' if num_posts > 1 else '')

forum_abbrevs = {
	'Serious Hardware / Software Crap': 'SHSC',
	'The Cavern of COBOL': 'CoC',
	'General Bullshit': 'GBS',
	'Haus of Tech Support': 'HoTS'
}
commands = {"sa": somethingawful, "somethingawful": somethingawful}
triggers = [(regex, urltranslatesa)]