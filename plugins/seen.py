from __future__ import division
#from __future__ import print_function
from __future__ import unicode_literals

import time
import datetime
from util import timesince


from botmily.db import db

# Literally match any message from anyone:
regex = r'(.+)'

def getdelta(t):
    delta = timesince.timesince(t) + " ago"
    # Check if it's been over a month since we saw them:
    days = datetime.timedelta(seconds=(time.time() - t)).days
    # Consider hiding this is it's been fewer than some number of days?
    if days >= 0:
        t = int(t)
        dt = datetime.datetime.fromtimestamp(t)
        delta = delta + " (" + dt.__str__() + ")"
    
    return delta

def seeninput(message_data, bot):
    # This could be improved but it doesn't matter:
    db.execute("create table if not exists seen(name text, time integer, quote text, chan text, primary key(name, chan))")
    db.execute("replace into seen(name, time, quote, chan) values (:name, :time, :quote, :chan)", {"name": message_data["nick"], "time": int(time.time()), "quote": message_data["message"], "chan": message_data['channel']})
    db.commit()
    pass

def seen(message_data, bot):
    searchname = message_data['parsed'].strip()
    chan = message_data['channel']

    if searchname.lower() == bot.nickname.lower(): # user is looking for us, being a smartass
        return "You need to get your eyes checked."

    if searchname.lower() == message_data['nick'].lower():
        return "Have you looked in a mirror lately?"

    last_seen = db.execute("select name, time, quote from seen where name like ? and chan = ?", (searchname, chan)).fetchone()
    
    if last_seen:
        reltime = getdelta(last_seen[1])
        if last_seen[0] != searchname.lower():  # for glob matching
            searchname = last_seen[0]
        return '%s was last seen %s saying: %s' % \
                    (searchname, reltime, last_seen[2])
    else:
        return "I've never seen %s" % searchname

commands = {"seen": seen}
triggers = [(regex, seeninput)]