from __future__ import division
#from __future__ import print_function
#from __future__ import unicode_literals

import time
import datetime
import math
from util import timesince, urlnorm

from botmily.db import db

# regex for detecting websites
regex = r'([a-zA-Z]+://|www\.)[^ ]+'

# Some kind of ignored url stuff that idk what is but whatever:
ignored_urls = [urlnorm.normalize("http://google.com")]

expiration_period = 60 * 60 * 24  # 1 day

def db_init(db):
    db.execute("create table if not exists urlhistory"
                 "(chan, url, nick, time)")
    db.commit()

def insert_history(db, chan, url, nick):
    now = time.time()
    db.execute("insert into urlhistory(chan, url, nick, time) "
                 "values(?,?,?,?)", (chan, url, nick, time.time()))
    db.commit()

def get_history(db, chan, url):
    db.execute("delete from urlhistory where time < ?",
                 (time.time() - expiration_period,))
    return db.execute("select nick, time from urlhistory where "
            "chan=? and url=? order by time desc", (chan, url)).fetchall()


def getdelta(t):
    # Make it easy to change this if we have to;
    delta = timesince.timesince(t)
    return delta

def nicklist(nicks):
    nicks = sorted(dict(nicks), key=unicode.lower)
    if len(nicks) <= 2:
        return ' and '.join(nicks)
    else:
        return ', and '.join((', '.join(nicks[:-1]), nicks[-1]))


def format_reply(history):
    if not history:
        return

    last_nick, recent_time = history[0]
    last_time = getdelta(recent_time)

    if len(history) == 1:
        return "%s linked that %s ago." % (last_nick, last_time)

    hour_span = math.ceil((time.time() - history[-1][1]) / 3600)
    hour_span = '%.0f hours' % hour_span if hour_span > 1 else 'hour'

    hlen = len(history)
    ordinal = ["once", "twice", "%d times" % hlen][min(hlen, 3) - 1]

    if len(dict(history)) == 1:
        last = "last linked %s ago" % last_time
    else:
        last = "last linked by %s %s ago" % (last_nick, last_time)

    return "that url has been posted %s in the past %s by %s (%s)." % (ordinal,
            hour_span, nicklist(history), last)

def urlinput(message_data, bot):
    # Verify the database exists;
    db_init(db)

    # normalise the url
    url = urlnorm.normalize(message_data['re'].group().encode('utf-8'))

    if url not in ignored_urls:
        url = url.decode('utf-8')

        # Load our primitives from message_data
        chan = message_data['channel']
        nick = message_data['nick']

        history = get_history(db, chan, url)
        insert_history(db, chan, url, nick)
        if nick not in dict(history):
            return format_reply(history)


commands = {}
triggers = [(regex, urlinput)]