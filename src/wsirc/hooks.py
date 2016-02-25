import logging

class Hooks(object):
    def __init__(self, wsirc):
        self.wsirc = wsirc
        self.registered_hooks = {}

    def run_hooks(self, channel, msg):
        for h in self.registered_hooks[channel]:
            logging.debug("Running %s from %s", h.__name__, channel)
            h(self.wsirc, msg, self)

    def make_hook_cb(self, channel):
        def manager_cb(msg):
            self.run_hooks(channel, msg)
        return manager_cb

    def create_hook_channel(self, name):
        self.registered_hooks[name] = []

    def register_hook(self, fn, category = 'all'):
        if fn not in self.registered_hooks[category]:
            self.registered_hooks[category].append(fn)
            return True
        return False
