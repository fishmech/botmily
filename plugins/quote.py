# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import time
import random
import re

from botmily.db import db

LastSearch = {}
LastResults = {}
LastNum = {}

def retformat(num,total,row):
    return "Quote %d/%d" % (num+1,total) + ": (" + row[0] + ") " + row[1]

def quote(message_data, bot):
    global LastSearch, LastResults, LastNum

    db.execute("create table if not exists quote(sender text, quote text, time integer)")
    if message_data["parsed"][:4] == "add ":
        db.execute("insert into quote(sender, quote, time) values (:sender, :quote, :time)", {"sender": message_data["nick"], "quote": message_data["parsed"][4:], "time": int(time.time())})
        db.commit()
        # Clear out all caches;
        LastSearch = {}
        LastResults = {}
        LastNum = {}
        return "Quote added."
    elif message_data["parsed"][:7] == "search ":

        # Seperate this data by channel;
        chan = message_data['channel']

        searchstring = message_data["parsed"]
        splitstring = searchstring.split()
        # If there are more than 3 parts, we are supplying a number we want to use perhaps, try to convert it to a number
        # If it succeeds, pop it from the search query
        num = 0
        if len(splitstring) >= 3:
            try:
                num = int(splitstring[-1])
                if num != 0:
                    # Valid number detected, remove this number:
                    splitstring.pop()
                    searchstring = " ".join(splitstring)
            except ValueError:
                num = 0
                pass

        # Check to see if this is the same as the last thing we searched so we can skip the DB pull:
        quotes = None
        IsReallyNext = False
        if chan in LastSearch:
            if searchstring == LastSearch[chan]:
                quotes = LastResults[chan]
                # Also sometimes this is really just someone doing the same search over and over to hear the next quote, so pretend to be next:
                IsReallyNext = True

        # If the list was not cached, do a DB pull:
        if quotes == None:
            quotes = db.execute("select sender, quote, time from quote where quote like :quote order by time ASC", {"quote": "%" + searchstring[7:] + "%"}).fetchall()

        # If results is now empty, don't update global dicts:
        total = len(quotes)
        if total == 0:
            return "Nothing found."

        # update cache dicts:
        LastSearch[chan] = searchstring
        LastResults[chan] = quotes
        
        # If num is out of range, select from the last value if we're really a 'next' command, or select randomly from range 0 - total
        if num <= 0 or num > total:
            if (IsReallyNext):
                num = ((LastNum[chan] + 1) % total)
            else: num = random.randrange(0,total) 
        else:
            # Otherwise substract one from supplied digit due to 0 indexing etc
            num -= 1

        # Update the cached value for this:
        LastNum[chan] = num
        
        # Select that quote row, and provied to formatting function
        row = quotes[num]
        return retformat(num,total,row)

    elif message_data["parsed"][:4] == "next":
        chan = message_data['channel']

        splitstring = message_data["parsed"].split()
        # If there are more than 2 parts, we are supplying a number we want to use probably
        num = 0
        if len(splitstring) >= 2:
            try:
                num = int(splitstring[-1])
            except ValueError:
                num = 0
                pass

        if not(chan in LastResults):
            return "No stored query. Try search instead!"
        quotes = LastResults[chan]

        total = len(quotes)
        if total == 0:
            return "No stored query. Try search instead!"

        # If num is out of range, recover last request and add 1 mod total:
        if num <= 0 or num > total:
            num = (LastNum[chan] + 1) % total
        else:
            # Otherwise substract one from supplied digit due to 0 indexing etc
            num -= 1

        LastNum[chan] = num

        row = quotes[num]
        return retformat(num,total,row)
    else:
        return "Use quote followed by 'add', 'search ...', 'search  ... #', 'next' or 'next #'!"

commands = {"quote": quote}
triggers = []

