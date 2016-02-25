import logging
import requests

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

def on_link(wsirc, msg, hooks):
    url = compose_url(msg.link)
    logging.warn(url)
    r = requests.get(url, timeout=1)
