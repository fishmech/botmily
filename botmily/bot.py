from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import asyncore
import pkgutil
import re
import socket
import sys
import traceback
import math
from botmily import config
from botmily import irc
import plugins

import select
import time

class bot():
	def __init__(self):
		self.server = config.server
		self.nickname = config.name
		self.realname = b"Botdrew https://github.com/kgc/botmily"
		self.channels = config.channels
		self.password = config.password
		self.sa_user = config.sa_user
		self.sa_password = config.sa_password
		self.timeout = config.timeout

		print("Initializing plugins...")
		self.commands = {}
		self.triggers = []
		for importer, modname, ispkg in pkgutil.iter_modules(plugins.__path__):
			print("Loading plugin " + modname)
			plugin = __import__("plugins." + modname, fromlist="hook")
			self.commands.update(plugin.commands)
			self.triggers.extend(plugin.triggers)


		Continue_State = True
		print("Attempting Connection! Mash Ctrl+C or whatever to exit.")
		while (Continue_State):
			Continue_State = self.connect()
			if Continue_State:
				try:
					print("Sleeping for 30 seconds before retrying...")
					time.sleep(30)
				except KeyboardInterrupt, err:
					Continue_State = False

		print("Exiting!")

	def drop(self, calling_irc_handler):
		# Prevent accidental rogue irc timers?
		print("DC message from " + calling_irc_handler.__str__())
		if self.irc is calling_irc_handler:
			self.socket.close()
			asyncore.close_all()
		else:
			print("Bot is ignoring out of date handler. Masti is bad at threading!")

	def connect(self):
		# we COULD close our old socket, if we have one, but... it should get closed in garbage collection so who cares?
		
		print("Connecting to:",self.server)

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			self.socket.connect((self.server, 6667))
		except socket.gaierror, err:
			print("Could not initiate connection!")
			return True

		self.irc = irc.irc_handler(self.socket, self , self.irc_error)

		print("Connection loop starting...")

		try:
			asyncore.loop()
		except select.error, err:
			pass
		except KeyboardInterrupt, err:
			print(" <- Keyboard Interupt detected, cancelling thread timers where possible...")
			self.irc.stop()
			return False

		return True

	def join(self, nick, user, host, channel):
		if nick == self.nickname:
			print("Joined channel " + channel)

	def privmsg(self, nick, user, host, channel, message):
		message_data = {"nick":    nick,
		                "user":    user,
		                "host":    host,
		                "channel": channel,
		                "message": message}
		command_match = re.match("\.([^ ]+) ?(.*)", message_data["message"])
		if command_match is not None:
			sent_command = command_match.group(1)
			message_data["parsed"] = command_match.group(2)
			possible_commands = []
			for command, function in self.commands.iteritems():
				if sent_command == command:
					possible_commands = [(command, function)]
					break
				if command.find(sent_command) == 0:
					possible_commands.append((command, function))
			if len(possible_commands) == 1:
				message_data["command"] = possible_commands[0][0]
				try:
					# Contact the bound function, supplying message data and self as a paramter
					output = possible_commands[0][1](message_data, self)
					if isinstance(output, str) or isinstance(output, unicode):
						self.say(nick, channel, output)
					elif isinstance(output, dict):
						# Merge the two dictionaries:
						o_dict = message_data.copy()
						o_dict.update(output)
						# Check we have the new output key
						if "output" in o_dict:
							self.say(o_dict["nick"], o_dict["channel"], o_dict["output"])
					else:
						# Fuck it, print it anyway:
						self.say(nick, channel, output)
				except Exception, E:
					print('Encountered error while processing commmand %s with input %s' %(str(possible_commands[0][1]),str(message_data)))
					traceback.print_exc()
					self.say(nick,channel,'I crashed while trying to deal with something you said @_@')

			if len(possible_commands) > 1:
				commands_formatted = []
				for command, function in possible_commands:
					commands_formatted.append("." + command)
				self.say(nick, channel, "Did you mean: " +
				                        ",".join(commands_formatted) + "?")
		for tup in self.triggers:
			trigger, function = tup
			if re.search(trigger, message_data["message"], re.I) is not None:
				message_data["re"] = re.search(trigger,
				                               message_data["message"], re.I)
				try:
					output = function(message_data, self)
					self.say(nick, channel, output)
				except Exception, E:
					print('Encountered error while processing trigger %s with input %s' %(str(function),str(message_data)))
					traceback.print_exc()
					self.say(nick,channel,'I crashed while trying to deal with something you said @_@')

		#for omni in self.allmsg:
				

	def say(self, nick, channel, output):
		maxsay = 400
		if output is None:
			return
		if len(output) > maxsay:
			maxval = int(math.ceil(len(output)/float(maxsay)))
			for x in range(0,maxval):
				if x < 2:
					self.do_msg(nick,channel,output[maxsay*x:maxsay*(x+1)])
				else:
					self.do_msg(nick,channel,output[maxsay*x:maxsay*(x+1) - 100] + "... %d lines additional ommitted!" % (maxval - 3))
					break
		else:
			self.do_msg(nick,channel,output)

	def do_msg(self,nick,channel,output):
		if output is None:
			return
		if self.nickname == channel:
			self.irc.privmsg(nick, output)
		else:
			self.irc.privmsg(channel, nick + ": " + output)

	def irc_error(self):
		print('Nasty error caught, trying to continue anyway , details below :  ')
		traceback.print_exc()
