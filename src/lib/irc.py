import socket, re, time, sys
from functions_general import *
import cron
import thread
import threading
import pickle
import shutil

mode_re = re.compile(r':jtv MODE #((?:[a-z][a-z0-9_]*)) (.)(.) ((?:[a-z][a-z0-9_]*))', re.IGNORECASE|re.DOTALL)
HR_IN_SEC = 60*60

def set_init(d, name):
	if name not in d:
		d[name] = set()
		
def dict_init(d, name):
	if name not in d:
		d[name] = {}
		
def safe_dict_get(d, mem):
	try:
		return d[mem]
	except:
		return None

class info(object):
	filename = "info.db"
	channels = {}
	users = {}
	def __init__(self, line):
		self.command = line[1].strip(":")
		if self.command == "PRIVMSG":
			self.channel = "#"+line[2]
			self.subject = line[4]
			self.subcommand = line[3].strip(":")
			self.arg = line[5]
		elif self.command == "MODE":
			self.channel = line[2]
			self.subject = line[4]
			self.subcommand = None
			self.arg = line[3]
		set_init(self.channels, self.channel)
		self.curr_channel = self.channels[self.channel]
		dict_init(self.users, self.subject)
		self.curr_user = self.users[self.subject]
		
	def print_(self):
		print self.__dict__
		
	def handle(self):
		if self.subcommand:
			if self.subcommand == "SPECIALUSER":
				dict_init(self.curr_user, self.subcommand)
				self.curr_user[self.subcommand][self.arg][self.channel] = time.time()
			else:
				self.curr_user[self.subcommand] = self.arg
		elif self.command == "MODE":
			if self.arg == "+o":
				self.curr_channel.add(self.subject)
			elif self.arg == "-o":
				self.curr_channel.remove(self.subject)
		else:
			print "Unrecognised",
			self.print_()
		info.save()
		
	@staticmethod
	def save():
		pickle.dump((info.channels, info.users), open(info.filename, "w"))
		
	@staticmethod
	def backup():
		try:
			shutil.copy(info.filename, info.filename+".bak")
		except Exception as e:
			print e
		
	@staticmethod
	def load():
		info.backup()
		try:
			f = pickle.load(open(info.filename, "r"))
		except:
			print "No existing DB to load"
		else:
			info.channels = f[0]
			info.users = f[0]
		
	@staticmethod
	def get_info(user):
		special = safe_dict_get(info.users[user], "SPECIALUSER")
		is_mod = [x for x in info.channels if user in info.channels[x]]
		
		return special,is_mod
		
	@staticmethod
	def is_sub(user, channel):
		s, mod = info.get_info(user)
		
		return  s != None and \
				"subscriber" in s and \
				channel in s["subscriber"] and \
				(time.time() - s["subscriber"][channel]) < HR_IN_SEC
		
	@staticmethod
	def is_mod(user, channel):
		s, mod = info.get_info(user)
		
		return channel in mod
info.load()

class irc:
	def __init__(self, config):
		self.config = config
		self._lock = threading.Lock()
	
	def check_for_connected(self, data):
		if re.match(r'^:.+ 001 .+ :connected to TMI$', data):
			return True
	
	def check_for_ping(self, data):
		if data[:4] == "PING": 
			self._lock.acquire()
			self.sock.send('PONG')
			self._lock.release()
	
	def check_login_status(self, data):
		if re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data):
			return False
		else:
			return True
	def parse_data(self, data):
		for d in data.split("\r\n"):
			self.parse_line(d)
		return
		
	def parse_line(self, line):
		line = line.strip(":\n\r")
		line = line.split()
		if line:
			if line[0] == "jtv":
				i = info(line)
				i.handle()
				print info.get_info(i.subject)
			elif line[0].startswith("jtv!"):
				pass
				# print "Twitch Message"
				# print line[1:]
			elif line[0].startswith("c2d2_."):
				pass
				# print "Me Message"
				# print line[1:]
			else:
				pass
				# print line
		
	def send_message(self, channel, message):
		self._lock.acquire()
		self.sock.send('PRIVMSG %s :%s\n' % (channel, message.encode('utf-8')))
		self._lock.release()

	def get_irc_socket_object(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(10)
		
		self.sock = sock
		
		try:
			sock.connect((self.config['server'], self.config['port']))
		except:
			pp('Cannot connect to server (%s:%s).' % (self.config['server'], self.config['port']), 'error')
			sys.exit()
		
		sock.settimeout(None)
		
		self._lock.acquire()
		sock.send('USER %s\r\n' % self.config['username'])
		sock.send('PASS %s\r\n' % self.config['oauth_password'])
		sock.send('NICK %s\r\n' % self.config['username'])
		self._lock.release()
		
		if self.check_login_status(sock.recv(1024)):
			pp('Login successful.')
		else:
			pp('Login unsuccessful. (hint: make sure your oauth token is set in self.config/self.config.py).', 'error')
			sys.exit()
			
		self.join_channels(self.channels_to_string(self.config['channels']))
		
		
		return sock
		
	def channels_to_string(self, channel_list):
		return ','.join(channel_list)
		
	def join_channels(self, channels):
		pp('Joining channels %s.' % channels)
		self._lock.acquire()
		self.sock.send('JOIN %s\r\n' % channels)
		self.sock.send('TWITCHCLIENT 1\r\n')
		self._lock.release()
		pp('Joined channels.')
		
	def leave_channels(self, channels):
		pp('Leaving chanels %s,' % channels)
		self._lock.acquire()
		self.sock.send('PART %s\r\n' % channels)
		self._lock.release()
		pp('Left channels.')