import re
import logging

from libs import muirc

LINK_RE = re.compile(r"((?:https\:\/\/)|(?:http\:\/\/)|(?:www\.))?([a-zA-Z0-9\-\.]+\.[a-zA-Z]{1,3}(?:\??)[a-zA-Z0-9\-\._\?\,\'\/\\\+&%\$#\=~]+)", re.IGNORECASE|re.DOTALL)

def list_get_default(s, index, default=None):
	return s[index] if len(s) > index else default

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
