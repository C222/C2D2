import logging
import requests
import httplib
import urllib3

requests.packages.urllib3.disable_warnings()

def compose_url(groups):
	url = groups[1]
	if groups[0] is not None:
		url = groups[0] + url
	else:
		url = "http://" + url
	return url

def on_chat(wsirc, msg, hooks):
	logging.debug("%s: %s: %s", wsirc.channel, msg.name, msg.chat)
	if msg.check_for_link():
		hooks.run_hooks("link", msg)

def on_command(wsirc, msg, hooks):
	return

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
