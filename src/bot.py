"""
Simple IRC Bot for Twitch.tv

Developed by Aidan Thomson <aidraj0@gmail.com>
"""

import lib.irc as irc_
from lib.functions_general import *
import shutil
import json
import threading
import time
import sched

PROMPT = "~"

is_command = lambda x: (x.startswith(PROMPT) and len(x)>len(PROMPT))

def uniquify(x):
	return list(set(x))

class Roboraj:

	def __init__(self, config):
		self.config = config
		self.irc = irc_.irc(config)
		self.socket = self.irc.get_irc_socket_object()
		self.s = sched.scheduler(time.time, time.sleep)
		self.commands = {
			"leave" : self.leave,
		}
		
		try:
			self.modes = json.load(open(config['file']+".modes", "r"))
			try:
				shutil.copy(config['file']+".modes", config['backup']+".modes")
			except Exception as e:
				print e
		except:
			self.modes = {}
		
		try:
			self.db = json.load(open(config['file'], "r"))
			try:
				shutil.copy(config['file'], config['backup'])
			except Exception as e:
				print e
		except:
			self.db = {}
		
	def leave(self, channel, message):
		self.irc.send_message(channel, "[Bye]")
		json.dump(self.db, open(self.config['file'],"w"))
		json.dump(self.modes, open(self.config['file']+".modes","w"))
		time.sleep(1)
		exit()
		
	def add_mode(self, g):
		print g
		if g:
			if g[0] not in self.modes:
				self.modes[g[0]] = {}
			if g[3] not in self.modes[g[0]]:
				self.modes[g[0]][g[3]] = []
			if g[1] == '-':
				self.modes[g[0]][g[3]] += [g[2]]
			else:
				try:
					self.modes[g[0]][g[3]].remove(g[2])
				except:
					print "!"
			print self.modes
			self.modes[g[0]][g[3]] = uniquify(self.modes[g[0]][g[3]])
			json.dump(self.modes, open(self.config['file']+".modes","w"))
		return
		
	def update_db(self, user, msg):
		if user not in self.db:
			self.db[user] = []
		for m in msg.split(" "):
			self.db[user] += [m]
		self.db[user] = uniquify(self.db[user])
		json.dump(self.db, open(self.config['file'],"w"))
		
		return
	
	def run(self):
		irc = self.irc
		sock = self.socket
		config = self.config
		
		for c in config['channels']:
			irc.send_message(c, "[{} has joined. oshi9]".format(config['username']))
			irc.send_message(c, ".mods".format(config['username']))
		
		while True:
			time.sleep(.01)
			data = sock.recv(config['socket_buffer_size']).rstrip()
			
			if len(data) == 0:
				pp('Connection was lost, reconnecting.')
				sock = self.irc.get_irc_socket_object()
			
			# if config['debug']:
				# print repr(data)
			
			# check for ping, reply with pong
			irc.check_for_ping(data)
			
			irc.parse_data(data)