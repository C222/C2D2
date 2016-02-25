import websocket
import thread
import time
import logging
import random
import multiprocessing
import platform
import signal
import re

from libs import muirc
from credentials import *
import hooks
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

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger('requests').setLevel(logging.CRITICAL)
logging.getLogger('requests.packages').setLevel(logging.CRITICAL)
logging.getLogger('requests.packages.urllib3').setLevel(logging.CRITICAL)
logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.CRITICAL)
logging.getLogger('requests.packages.urllib3.poolmanager').setLevel(logging.CRITICAL)
logging.getLogger('requests.packages.urllib3.util').setLevel(logging.CRITICAL)
logging.getLogger('requests.packages.urllib3.util.retry').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('urllib3.connectionpool').setLevel(logging.CRITICAL)
logging.getLogger('urllib3.poolmanager').setLevel(logging.CRITICAL)
logging.getLogger('urllib3.util').setLevel(logging.CRITICAL)
logging.getLogger('urllib3.util.retry').setLevel(logging.CRITICAL)

LINK_RE = None

def list_get_default(s, index, default=None):
	return s[index] if len(s) > index else default


def spawn_bot(channel, limit):
	global LINK_RE
	chat = WS_IRC(channel, limit)
	if LINK_RE is None:
		logging.info("Compiling RE")
		LINK_RE = re.compile(r"((?:https\:\/\/)|(?:http\:\/\/)|(?:www\.))?([a-zA-Z0-9\-\.]+\.[a-zA-Z]{1,3}(?:\??)[a-zA-Z0-9\-\._\?\,\'\/\\\+&%\$#\=~]+)", re.IGNORECASE|re.DOTALL)
	chat.start()


def sem_val(sem):
	return int(str(sem).split("=")[1].split(")")[0])

def parse_message(msg):
	msg = msg.split(":tmi.twitch.tv")
	msg[0] = msg[0].split(";")
	return msg

class Message(object):
	def __init__(self, msg):
		self.msg = msg
		self.parse()
		self.link = None
		self.link_re = LINK_RE

	def parse(self):
		if self.msg.startswith("@"):
			split = self.msg.index(" :")
			self.tags = self.msg[1:split].split(";")
			self.tags = {x.split("=")[0]: x.split("=")[1] for x in self.tags}
			self.msg = self.msg[split:].lstrip()
		else:
			self.tags = {}
		self.msg = muirc.translate(self.msg)
		self.name = self.tags.get("display-name", False)
		if not self.name:
			self.name = self.msg.get("nick", None)
		self.chat = self.msg.get("params", [])
		self.chat = list_get_default(self.chat, 1)

	def check_for_link(self):
		m = self.link_re.search(self.chat)
		if m:
			self.link = m.groups()
			return True
		else:
			return False

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

if __name__ == "__main__":
	if platform.system() == "Windows":
		multiprocessing.freeze_support()

	limit = multiprocessing.Semaphore(30)
	channels = ["c222_", "iwinuloselol"]
	processes = []

	def end_clean(num, frame):
		for p in processes:
			p.terminate()
		for p in processes:
			p.join()
		exit()

	signal.signal(signal.SIGINT, end_clean)

	for c in channels:
		p = multiprocessing.Process(target=spawn_bot, args=(c, limit))
		processes.append(p)

	for p in processes:
		p.start()
	
	while True:
		time.sleep(30)
		logging.debug(sem_val(limit))
		while sem_val(limit) < 30:
			limit.release()
