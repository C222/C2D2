'''Functions to handle specific events and commands

Attributes:
	COMMANDS: A dictionary of command-word and function pairs
'''

import logging
import requests
import httplib
import urllib3
from datetime import datetime
import time
import platform

import config

if platform.system() == "Windows":
	requests.packages.urllib3.disable_warnings()

###########
# Utility #
###########

def permissions(mod=False, sub=False):
	'''Decorator to restrict the use of a command.
	
	Channel owners are always allowed to use a command.
	
	Args:
		mod: Whether or not to allow mods to use the command
		sub: Whether or not to allow subscribers to use the command
	
	Returns:
		A function that only runs only if the message sender meets specific requirements.
	'''
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
	'''Converts a tuple of groups from a Message.link object into a possibly valid URL.
	
	Args:
		groups: The tuple from the links member in a Message object.
	
	Returns:
		A string that is possibly a valid URL.
	'''
	url = groups[1]
	if groups[0] is not None:
		url = groups[0] + url
	if not (url.lower().startswith("http://") or url.lower().startswith("https://")):
		url = "http://" + url
	return url

def check_owner(wsirc, msg):
	'''Check if the message sender is the owner of the current channel.
	
	Args:
		wsirc: The WS_IRC object connected to a channel.
		msg: The message to check the owner of.
	
	Returns:
		True if the sender of the message is the owner of the channel.
	'''
	return wsirc.channel == msg.name.lower()

def compare_url(a, b):
	'''Compare two urls to see if they're from the same domain(ish).
	
	Args:
		a: A string containing a URL.
		b: A string containing a URL.
	
	Returns:
		True if the URL domains are similar enough.
	'''
	a = a.split("/")[2].replace(".", "")
	b = b.split("/")[2].replace(".", "")

	return (a in b) or (b in a)

def humanize(ln):
	ret = ln.split("/")[2]
	ret = ret.replace(".", "(.)")
	ret = "[Shortened link to {} detected MrDestructoid ]".format(ret)
	return ret

############
# COMMANDS #
############

@permissions(mod=True, sub=True)
def cmd_ban(wsirc, msg, hooks):
	args = msg.chat.lstrip(config.PROMPT).split(" ")[1:]
	wsirc.chat("{} has been banned from {}. Kappa".format("".join(args), wsirc.channel))

def cmd_imgur(wsirc, msg, hooks):
	args = msg.chat.lstrip(config.PROMPT).split(" ")[1:]

	try:
		r = requests.get("https://api.imgur.com/2/image/{}".format(args[0]))
	except Exception as e:
		logging.exception(e)
	else:
		logging.info(r.json())

@permissions(mod=True, sub=True)
def cmd_streamer(wsirc, msg, hooks):
	args = msg.chat.lstrip(config.PROMPT).split(" ")[1:]

	try:
		users = requests.get("https://api.twitch.tv/kraken/users/{}".format(args[0]))
		channels = requests.get("https://api.twitch.tv/kraken/channels/{}".format(args[0]))
	except Exception as e:
		logging.exception(e)
	else:
		users = users.json()
		channels = channels.json()
		if users.get("status", "200") != "200" and channels.get("status", "200") != "200":
			return
		else:
			joined = datetime.strptime(users["created_at"],"%Y-%m-%dT%H:%M:%SZ")
			since = int((((datetime.utcnow() - joined).days)/365.0) * 12.0)
			wsirc.chat("{}: {}".format(users.get("display_name", args[0]), users.get("bio", "")))
			wsirc.chat("They have been on Twitch for {} months and they last played {}.".format(since, channels.get("game", "nothing")))
			wsirc.chat("Follow them at {}".format(channels["url"]))

@permissions(mod=True, sub=True)
def cmd_status(wsirc, msg, hooks):
	args = msg.chat.lstrip(config.PROMPT).split(" ")[1:]

	try:
		streams = requests.get("https://api.twitch.tv/kraken/streams/{}".format(args[0]))
	except Exception as e:
		logging.exception(e)
	else:
		streams = streams.json()
		if streams.get("status", "200") != "200":
			return
		else:
			if streams["stream"] is None:
				wsirc.chat("{} is currently offline.".format(args[0]))
			else:
				wsirc.chat("{} is currently streaming {} at {}p@{}fps to {} viewers.".format(
				streams["stream"]["channel"]["display_name"],
				streams["stream"]["game"],
				streams["stream"]["video_height"],
				int(streams["stream"]["average_fps"]),
				streams["stream"]["viewers"]))

def cmd_potatoes(wsirc, msg, hooks):
	wsirc.chat("Potatoes Potatoes Potatoes <3")

def cmd_botlove(wsirc, msg, hooks):
	wsirc.chat("!hug Nightbot")

def cmd_about(wsirc, msg, hooks):
	wsirc.chat("I am C2D2, an experimental bot. I have a select few commands available and I expand shortened links. My source code is at https://github.com/C222/C2D2 . If I break, complain to C222_. Channel owners can make me leave with '~part'")

@permissions()
def cmd_part(wsirc, msg, hooks):
	wsirc.chat("Bye!")
	wsirc.run = False
	exit()

COMMANDS = {
	"ban": cmd_ban,
	"imgur": cmd_imgur,
	"status": cmd_status,
	"streamer": cmd_streamer,
	"potatoes": cmd_potatoes,
	"about": cmd_about,
	"part": cmd_part,
	"botlove": cmd_botlove
}

##########
# EVENTS #
##########

def on_chat(wsirc, msg, hooks):
	if msg.name.lower() in config.BOTS:
		return
	logging.info("%s: %s: %s", wsirc.channel, msg.name, msg.chat)
	if msg.check_for_link():
		hooks.run_hooks("link", msg)
	if msg.chat.startswith(config.PROMPT):
		hooks.run_hooks("command", msg)

COOLDOWNS = {}

def on_command(wsirc, msg, hooks):
	command = msg.chat.lstrip(config.PROMPT).split(" ")[0]

	lasttime = COOLDOWNS.get(command, 0)
	sincelast = time.time() - lasttime

	if command in COMMANDS and sincelast > config.COOLDOWN_WAIT:
		COOLDOWNS[command] = time.time()
		COMMANDS[command](wsirc, msg, hooks)

def on_link(wsirc, msg, hooks):
	if msg.tags['mod'] == '1':
		return
	url = compose_url(msg.link)
	logging.warn("%s detected from %s", url, msg.name)
	try:
		r = requests.get(url, timeout=10)
	except Exception as e:
		logging.error("%s on %s", e, url)
	else:
		if not compare_url(url, r.url):
			wsirc.chat(humanize(r.url))
			logging.info("%s returned %s from %s", url, r.status_code, r.url)
