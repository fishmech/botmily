# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import time

from botmily.db import db

def quote(message_data, bot):
    return message_data.__str__()

commands = {"test": quote}
triggers = []

