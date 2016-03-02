'''
	Created February 25, 2016
	Author: C222
'''

import random
import hooks
import logging
import websocket
import thread
import time

from message import Message
from credentials import *
import handlers
import config
if config.CASSANDRA_LOGGING_ENABLE:
	from cassandra_connection import CassandraConnection

class WS_IRC(object):
	'''
	Attributes:
		channel: The IRC channel joined.
		URL: The ws_irc server connected to.
		run: Thread run flag
		hooks: The Hooks object.
	'''
	def __init__(self, channel, limit):
		'''A connection to a Twitch WebSocket IRC server

		The connection goes to a randomly-chosen server from TWITCH_SERVERS.

		Args:
			channel: string of the IRC channel to join upon connection
			limit: a multiprocessing.Semaphore to limit the # of messages/second
				from a single connection
		'''
		self.channel = channel
		self.URL = random.choice(config.TWITCH_SERVERS)
		self.run = False
		self.limit = limit
		self.hooks = hooks.Hooks(self)
		self.hooks.create_hook_channel("chat")
		self.hooks.create_hook_channel("link")
		self.hooks.create_hook_channel("command")
		self._registered = False
		self.cass_connect = None

	@staticmethod
	def is_symbol(c):
		'''Test if a character is a non-alphanum.

		Args:
			c: a character

		Returns:
			True if the character is a non-alphanum.
		'''
		return c not in (string.ascii_letters + string.digits)

	def start(self):
		'''Start the running thread of the SW_IRC object.

		The Thread runs forever while self.run is True.
		'''
		self.run = True
		logging.info("Connecting to %s", self.URL)
		self.ws = websocket.WebSocketApp(self.URL,
							  on_message=self.on_message,
							  on_error=self.on_error,
							  on_close=self.on_close)
		self.ws.on_open = self.on_open
		self.ws.run_forever()

	def on_open(self, ws):
		'''Callback for the WebSocketApp open event

		Args:
			ws: the WebSocketApp object
		'''
		thread.start_new_thread(self.run_loop, ())

	def on_close(self, ws):
		'''Callback for the WebSocketApp close event

		Args:
			ws: the WebSocketApp object
		'''
		logging.warn("Closed connection to %s", self.channel)

	def on_error(self, ws, error):
		'''Callback for the WebSocketApp error event

		Args:
			ws: the WebSocketApp object
			error: the error thrown.
		'''
		logging.error("%s", error)

	def on_message(self, ws, message):
		'''Callback for the WebSocketApp message event

		Args:
			ws: the WebSocketApp object
			message: the raw string of the message recieved
		'''
		if message.startswith("PING"):
			self.send("PONG\n", True)
		msg = Message(message)
		if msg.chat is not None:
			self.hooks.run_hooks("chat", msg)

	def send(self, msg, blocking=False, debug=True):
		'''Send a message to the WebSocket IRC server

		Args:
			msg: string to send to the server
			blocking: whether or not to wait on the limiting semaphore or fail
				upon not acquiring it
			debug: whether or not to log the outgoing string at debug level.
				This is useful for things like not logging the OAuth password.

		Returns:
			True if the send succeeded
		'''
		if debug:
			logging.debug("Sending %s", msg)
		if blocking:
			self.limit.acquire()
			self.ws.send(msg)
			return True
		else:
			if self.limit.acquire(False):
				self.ws.send(msg)
				return True
			else:
				return False

	def chat(self, msg, blocking=False):
		'''Send a preformatted chat message to the WebSocket IRC channel

		Args:
			msg: string to chat to the channel
			blocking: whether or not to wait on the limiting semaphore or fail
				upon not acquiring it

		Returns:
			True if the chat succeeded
		'''
		structure = "@sent-ts={} PRIVMSG #{} :{}\n"
		return self.send(structure.format(str(int(time.time())), self.channel, msg), blocking)

	def register_hooks(self):
		if not self._registered:
			self.hooks.register_hook(handlers.on_chat, "chat")
			self.hooks.register_hook(handlers.on_link, "link")
			self.hooks.register_hook(handlers.on_command, "command")
			if config.CASSANDRA_LOGGING_ENABLE:
				self.cass_connect = CassandraConnection()
				self.hooks.register_hook(self.cass_connect.on_chat, "chat")
			self._registered = True

	def run_loop(self):
		'''The function that runs inside the thread after open

		Will run until self.run is False and the WebSocket closes.
		'''
		while self.run:
			self.send("CAP REQ :twitch.tv/tags twitch.tv/commands\n", True)
			logging.info("Logging in as %s", NICK)
			self.send("PASS {}\n".format(OAUTH), True, False)
			self.send("NICK {}\n".format(NICK), True)
			time.sleep(1)
			logging.info("Joining %s", self.channel)
			self.send("JOIN #{}\n".format(self.channel), True)
			self.register_hooks()
			while True:
				time.sleep(.1)
			ws.close()
