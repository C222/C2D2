import websocket
import thread
import time
import logging
import random
import multiprocessing
import platform
import signal

from credentials import *

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

def spawn_bot(channel, limit):
	chat = WS_IRC(channel, limit)
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
		
	def parse(self):
		divide = ":tmi.twitch.tv "
		if "user-type= :" in self.msg:
			divide = "user-type= :"
		msg = self.msg.split(divide)
		tag_string = msg[0]
		if len(msg) > 1:
			self.text = msg[1]
		else:
			self.text = None
			
		self.tags = {}
		for t in tag_string.split(";"):
			s = t.split("=")
			if s[0]:
				if len(s) > 1:
					self.tags[s[0]] = s[1]
				else:
					self.tags[s[0]] = None
		
		if self.text and "PRIVMSG" in self.text:
			msg = self.text.replace(self.tags['display-name'].lower(), "")
			msg = msg.replace("!@.tmi.twitch.tv PRIVMSG #", "")
			msg = msg.split(" :")
			self.channel = msg[0]
			self.chat = " :".join(msg[1:]).rstrip("\n\r")
			self.user = self.tags['display-name']
		else:
			self.channel = None
			self.chat = None
			self.user = None
	
class WS_IRC(object):
	def __init__(self, channel, limit):
		self.channel = channel
		self.URL = random.choice(TWITCH_SERVERS)
		self.run = False
		self.limit = limit
		
	def start(self):
		self.run = True
		logging.info("Connecting to %s", self.URL)
		self.ws = websocket.WebSocketApp(self.URL,
							  on_message = self.on_message,
							  on_error = self.on_error,
							  on_close = self.on_close)
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
		if msg.chat:
			logging.info("%s: %s", self.channel, msg.tags)
			logging.info("%s: %s: %s", self.channel, msg.user, msg.chat)
		else:
			logging.info("%s: %s", self.channel, msg.tags)
			logging.info("%s: %s", self.channel, msg.text)
			logging.info("%s: %s", self.channel, msg.msg)
		
	def send(self, msg, blocking=False):
		if blocking:
			self.limit.acquire()
			self.ws.send(msg)
		else:
			if self.limit.acquire(False):
				self.ws.send(msg)
				
	def run_loop(self):
		while self.run:
			self.send("CAP REQ :twitch.tv/tags twitch.tv/commands\n", True)
			logging.info("Logging in as %s", NICK)
			self.send("PASS {}\n".format(OAUTH), True)
			self.send("NICK {}\n".format(NICK), True)
			time.sleep(1)
			logging.info("Joining %s", self.channel)
			self.send("JOIN #{}\n".format(self.channel), True)
			while True:
				time.sleep(.1)
			ws.close()
			
if __name__ == "__main__":
	if platform.system() == "Windows":
		multiprocessing.freeze_support()
		
	limit = multiprocessing.Semaphore(30)
	channels = ["fuzzyfreaks", "iwinuloselol", "c222_", "xsmak"]
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
		logging.info(sem_val(limit))
		while sem_val(limit) < 30:
			limit.release()