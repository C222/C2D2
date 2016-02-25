import logging
import requests
import httplib
import urllib3

requests.packages.urllib3.disable_warnings()

PROMPT = "|"

def permissions(mod=False, sub=False):
	def fun_check(function):
		def perm_function(wsirc, msg, hooks):
			if mod and msg.tags['mod'] == '1':
				function(wsirc, msg, hooks)
				return
			if sub and msg.tags['subscriber'] == '1':
				function(wsirc, msg, hooks)
				return
			if check_owner(wsirc, msg):
				function(wsirc, msg, hooks)
				return
		return perm_function
	return fun_check

def compose_url(groups):
	url = groups[1]
	if groups[0] is not None:
		url = groups[0] + url
	else:
		url = "http://" + url
	return url

def check_owner(wsirc, msg):
	return wsirc.channel == msg.name.lower()

def on_chat(wsirc, msg, hooks):
	logging.debug("%s: %s: %s", wsirc.channel, msg.name, msg.chat)
	if msg.check_for_link():
		hooks.run_hooks("link", msg)
	if msg.chat.startswith(PROMPT):
		hooks.run_hooks("command", msg)

def on_command(wsirc, msg, hooks):
	command = msg.chat.split(" ")
	wsirc.chat("As you wish, {} OpieOP".format(msg.name))

def on_link(wsirc, msg, hooks):
	url = compose_url(msg.link)
	logging.warn(url)
	try:
		r = requests.get(url, timeout=5)
	except httplib.InvalidURL as e:
		pass
	except requests.exceptions.ConnectTimeout as e:
		pass
	else:
		if url != r.url:
			wsirc.chat("{} linked to {} DansGame".format(msg.name, r.url))
			logging.info("%s returned %s from %s", url, r.status_code, r.url)
