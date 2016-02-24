import logging

def on_chat(wsirc, msg, hooks):
    logging.debug("%s: %s: %s", wsirc.channel, msg.name, msg.chat)
    if msg.check_for_link():
        hooks.run_hooks("link", msg)

def on_link(wsirc, msg, hooks):
    logging.warn(msg.link)
