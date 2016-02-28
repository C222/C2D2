'''
Change the settings here before running the bot and remove the ".CHANGEME" from
the filename.

Attributes:
	CHANNELS: The channels to connect to.
	BURST_RATE_30: The maximum messages that can be sent in 30 seconds.
	TWITCH_SERVERS: Pool of Twitch ws_irc servers to connect to.
	PROMPT: The character all commands start with.
	BOTS: Nicknames to completely ignore.
	COOLDOWN_WAIT: Number of seconds before a command can be repeated.
'''

CHANNELS = ["c222_", "oshi7", "iwinuloselol"]
BURST_RATE_30 = 30

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

PROMPT = "~"
BOTS = ["nightbot", "iwinzbot", "twitchnotify"]
COOLDOWN_WAIT = 60