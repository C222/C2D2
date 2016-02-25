import websocket
import thread
import time
import logging
import random
import multiprocessing
import platform
import signal
import re
import string

from libs import muirc
from credentials import *
from wsirc.wsirc import WS_IRC

logging.getLogger().setLevel(logging.INFO)

def spawn_bot(channel, limit):
	chat = WS_IRC(channel, limit)
	chat.start()


def sem_val(sem):
	return int(str(sem).split("=")[1].split(")")[0])

if __name__ == "__main__":
	if platform.system() == "Windows":
		multiprocessing.freeze_support()

	limit = multiprocessing.Semaphore(30)
	channels = ["c222_", "oshi7"]
	processes = []

	def end_clean(num, frame):
		for p in processes:
			p.terminate()
		for p in processes:
			p.join()
		exit()

	signal.signal(signal.SIGINT, end_clean)

	for c in channels:
		p = multiprocessing.Process(target=spawn_bot, args=(c, limit))
		processes.append(p)

	for p in processes:
		p.start()

	while True:
		time.sleep(30)
		logging.debug(sem_val(limit))
		while sem_val(limit) < 30:
			limit.release()
