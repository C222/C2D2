import random
import hooks
import logging
import websocket
import thread
import time

from message import Message
from credentials import *
import handlers

TWITCH_SERVERS = ["ws://192.16.64.174/",
				  "ws://192.16.64.175/",
				  "ws://192.16.64.176/",
				  "ws://192.16.64.177/",
				  "ws://192.16.64.178/",
				  "ws://192.16.64.179/",
				  "ws://192.16.64.205/",
				  "ws://192.16.64.206/",
				  "ws://192.16.64.207/",
				  "ws://192.16.64.208/",
				  "ws://192.16.64.209/",
				  "ws://192.16.64.210/",
				  "ws://192.16.64.211/"]

class WS_IRC(object):
	def __init__(self, channel, limit):
		self.channel = channel
		self.URL = random.choice(TWITCH_SERVERS)
		self.run = False
		self.limit = limit
		self.hooks = hooks.Hooks(self)
		self.hooks.create_hook_channel("chat")
		self.hooks.create_hook_channel("link")
		self.hooks.create_hook_channel("command")

	@staticmethod
	def is_symbol(c):
		return c not in (string.ascii_letters + string.digits)

	def start(self):
		self.run = True
		logging.info("Connecting to %s", self.URL)
		self.ws = websocket.WebSocketApp(self.URL,
							  on_message=self.on_message,
							  on_error=self.on_error,
							  on_close=self.on_close)
		self.ws.on_open = self.on_open
		self.ws.run_forever()

	def on_open(self, ws):
		thread.start_new_thread(self.run_loop, ())

	def on_close(self, ws):
		logging.warn("Closed connection to %s", self.channel)

	def on_error(self, ws, error):
		logging.error("%s", error)

	def on_message(self, ws, message):
		if message.startswith("PING"):
			self.send("PONG\n", True)
		msg = Message(message)
		if msg.chat is not None:
			self.hooks.run_hooks("chat", msg)

	def send(self, msg, blocking=False, debug=True):
		if debug:
			logging.debug("Sending %s", msg)
		if blocking:
			self.limit.acquire()
			self.ws.send(msg)
		else:
			if self.limit.acquire(False):
				self.ws.send(msg)

	def chat(self, msg, blocking=False):
		structure = "@sent-ts={} PRIVMSG #{} :{}\n"
		self.send(structure.format(str(int(time.time())), self.channel, msg), blocking)

	def run_loop(self):
		while self.run:
			self.send("CAP REQ :twitch.tv/tags twitch.tv/commands\n", True)
			logging.info("Logging in as %s", NICK)
			self.send("PASS {}\n".format(OAUTH), True, False)
			self.send("NICK {}\n".format(NICK), True)
			time.sleep(1)
			logging.info("Joining %s", self.channel)
			self.send("JOIN #{}\n".format(self.channel), True)
			self.hooks.register_hook(handlers.on_chat, "chat")
			self.hooks.register_hook(handlers.on_link, "link")
			self.hooks.register_hook(handlers.on_command, "command")
			while True:
				time.sleep(.1)
			ws.close()
