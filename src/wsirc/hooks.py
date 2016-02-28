import logging

class Hooks(object):
	'''A system to register callback functions into channels
	
	All callbacks are synchronous in the run_hooks call.
	
	Attributes:
		wsirc: The WS_IRC object to pass to the callbacks.
		registered_hooks: A dictionary of channel name and list of function pairs.
	'''
	def __init__(self, wsirc):
		self.wsirc = wsirc
		self.registered_hooks = {}

	def run_hooks(self, channel, msg):
		'''Run all functions in the specified channel.
		
		Args:
			channel: The name of the channel to run.
			msg: The Message object to pass to the callbacks.
		'''
		for h in self.registered_hooks[channel]:
			logging.debug("Running %s from %s", h.__name__, channel)
			h(self.wsirc, msg, self)

	def make_hook_cb(self, channel):
		'''Create a single function to run a specific channel.
		
		Args:
			channel: The name of the channel to run.
			
		Returns:
			A function that runs a specific channel's hooks and
			accepts a Message object as an argument.
		'''
		def manager_cb(msg):
			self.run_hooks(channel, msg)
		return manager_cb

	def create_hook_channel(self, name):
		'''Creates a hook channel with a new name, or clears an existing one.
		
		Args:
			name: The name to use.
		'''
		self.registered_hooks[name] = []

	def register_hook(self, fn, channel):
		'''Insert a function into the specified channel.
		
		Args:
			fn: The function to insert into the channel. It must
				accept three arguments: a WS_IRC object, a Message
				object, and a Hooks object.
			channel: The channel to insert the function into. The
				channel must have been created first using
				create_hook_channel.
		
		Returns:
			True if the function was sucessfully inserted into the channel.
		'''
		if fn not in self.registered_hooks[channel]:
			self.registered_hooks[channel].append(fn)
			return True
		return False
