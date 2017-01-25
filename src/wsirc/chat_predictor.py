import logging
import re
import string

import textblob

import config

CACHE_LIMIT = 3
WHITESPACE = re.compile(r'\W+')

def sanitize(message):
	message = filter(lambda c: c in string.printable,
					 message)
	WHITESPACE.sub(' ', message)
	return message.lower()

class Predictor(object):
	def __init__(self, c_name):
		self.c_name = c_name
		self.chat_cache = {}

	def on_chat(self, wsirc, msg, hooks):
		nick = msg.msg.get("nick")
		out = None

		if config.NLP_SENTIMENT:
			sentiment = textblob.TextBlob(sanitize(msg.chat)).sentiment
			if sentiment.polarity < -0.1:
				logging.info(sanitize(msg.chat))
				logging.info(sentiment)

		if nick in self.chat_cache:
			logging.info(len(self.chat_cache[nick]))
			if len(self.chat_cache[nick]) >= CACHE_LIMIT:
				out = self.chat_cache[nick].pop(0)

			self.chat_cache[nick].append(msg)

		else:
			self.chat_cache[nick] = [msg]

		if out is not None:
			logging.info("OUT: %s: %s", out.msg.get('nick'), out.chat)
