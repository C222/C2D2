import logging
import requests
import httplib
import urllib3
from datetime import datetime

requests.packages.urllib3.disable_warnings()

PROMPT = "|"

"""
Utility
"""

def permissions(mod=False, sub=False):
	def fun_check(function):
		def perm_function(wsirc, msg, hooks):
			if mod and msg.tags['mod'] == '1':
				function(wsirc, msg, hooks)
			elif sub and msg.tags['subscriber'] == '1':
				function(wsirc, msg, hooks)
			elif check_owner(wsirc, msg):
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

"""
COMMANDS
"""

@permissions(mod=True, sub=True)
def cmd_ban(wsirc, msg, hooks):
	args = msg.chat.lstrip(PROMPT).split(" ")[1:]
	wsirc.chat("{} has been banned from {}. Kappa".format("".join(args), wsirc.channel))

def cmd_imgur(wsirc, msg, hooks):
	args = msg.chat.lstrip(PROMPT).split(" ")[1:]
	
	try:
		r = requests.get("https://api.imgur.com/2/image/{}".format(args[0]))
	except Exception as e:
		logging.exception(e)
	else:
		logging.info(r.json())

@permissions(mod=True, sub=True)
def cmd_streamer(wsirc, msg, hooks):
	args = msg.chat.lstrip(PROMPT).split(" ")[1:]
	
	try:
		users = requests.get("https://api.twitch.tv/kraken/users/{}".format(args[0]))
		channels = requests.get("https://api.twitch.tv/kraken/channels/{}".format(args[0]))
	except Exception as e:
		logging.exception(e)
	else:
		users = users.json()
		channels = channels.json()
		if users.get("status", "200") == 404 or channels.get("status", "200") == 404:
			return
		else:
			joined = datetime.strptime(users["created_at"],"%Y-%m-%dT%H:%M:%SZ")
			since = int((((datetime.utcnow() - joined).days)/365.0) * 12.0)
			wsirc.chat("{}: {}".format(users["display_name"], users["bio"]))
			wsirc.chat("They have been on Twitch for {} months and they last played {}".format(since, channels["game"]))
			wsirc.chat("Follow them at {}".format(channels["url"]))
			
@permissions(mod=True, sub=True)
def cmd_status(wsirc, msg, hooks):
	args = msg.chat.lstrip(PROMPT).split(" ")[1:]
	
	try:
		streams = requests.get("https://api.twitch.tv/kraken/streams/{}".format(args[0]))
	except Exception as e:
		logging.exception(e)
	else:
		streams = streams.json()
		if streams.get("status", "200") == 404:
			return
		else:
			if streams["stream"] is None:
				wsirc.chat("{} is currently offline.".format(args[0]))
			else:
				wsirc.chat("{} is currently streaming {} at {}p@{} to {} viewers.".format(
				streams["stream"]["channel"]["display_name"],
				streams["stream"]["game"],
				streams["stream"]["video_height"],
				int(streams["stream"]["average_fps"]),
				streams["stream"]["viewers"]))
	

"""
EVENTS
"""
COMMANDS = {
	"ban": cmd_ban,
	"imgur": cmd_imgur,
	"status": cmd_status,
	"streamer": cmd_streamer
}
def on_chat(wsirc, msg, hooks):
	logging.debug("%s: %s: %s", wsirc.channel, msg.name, msg.chat)
	if msg.check_for_link():
		hooks.run_hooks("link", msg)
	if msg.chat.startswith(PROMPT):
		hooks.run_hooks("command", msg)

def on_command(wsirc, msg, hooks):
	command = msg.chat.lstrip(PROMPT).split(" ")[0]
	if command in COMMANDS:
		COMMANDS[command](wsirc, msg, hooks)

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
			