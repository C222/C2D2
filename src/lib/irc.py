import socket, re, time, sys
from functions_general import *
import cron
import thread
import threading

mode_re = re.compile(r':jtv MODE #((?:[a-z][a-z0-9_]*)) (.)(.) ((?:[a-z][a-z0-9_]*))', re.IGNORECASE|re.DOTALL)

class info(object):
	def __init__(self, line):
		print line
		self.command = line[1].strip(":")
		self.subject = line[3]
		self.args = line[4:]
		
	def print_(self):
		print self.command, self.subject, self.args

class irc:
	def __init__(self, config):
		self.config = config
		self._lock = threading.Lock()
	
	def check_is_command(self, message, valid_commands):
		for command in valid_commands:
			if command == message:
				return True
	
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
				info(line).print_()
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