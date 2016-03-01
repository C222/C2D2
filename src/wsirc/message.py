import re
import logging

from libs import muirc

LINK_RE = re.compile(r"((?:https\:\/\/)|(?:http\:\/\/)|(?:www\.))?([a-zA-Z0-9\-\.]+\.[a-zA-Z]{1,3}(?:\??)[a-zA-Z0-9\-\._\?\,\'\/\\\+&%\$#\=~]+)", re.IGNORECASE|re.DOTALL)

def list_get_default(s, index, default=None):
	return s[index] if len(s) > index else default

class Message(object):
	'''Representation for a single IRC message.
	
	Attributes:
		msg: Parsed dictionary if IRC message elements. Includes: nick, user, host, command, params
		link: A potential link detected in the message, otherwise None.
		link_re: Local reference to the copiled link regex used.
		tags: A dictionary representing the IRCv3 tags.
		chat: The chat message sent to the channel.
		name: the name of the sender of the message to the channel.
	'''
	def __init__(self, msg):
		'''
		Args:
			msg: the raw message string to be parsed.
		'''
		self.msg = msg
		self.link = None
		self.link_re = LINK_RE
		self.parse()
		self.tags = {}
		self.chat = None
		self.name = None

	def parse(self):
		'''Triggers the parsing of the message string.
		
		This usually takes place during construction.
		'''
		if self.msg.startswith("@"):
			split = self.msg.index(" :")
			self.tags = self.msg[1:split].split(";")
			self.tags = {x.split("=")[0]: x.split("=")[1] for x in self.tags}
			self.msg = self.msg[split:].lstrip()
		self.msg = muirc.translate(self.msg)
		self.name = self.tags.get("display-name", False)
		if not self.name:
			self.name = self.msg.get("nick", None)
		self.chat = self.msg.get("params", [])
		self.chat = list_get_default(self.chat, 1)

	def check_for_link(self):
		'''Triggers the regex detection of any links in the chat message.
		
		This usually takes place if there is a chat message.
		
		Returns: True if there is a link detected.
		'''
		m = self.link_re.search(self.chat)
		if m:
			self.link = m.groups()
			return True
		else:
			return False
