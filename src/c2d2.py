#!/usr/bin/python2

import time
import logging
import multiprocessing
import platform
import signal

from wsirc.wsirc import WS_IRC
import config

logging.getLogger().setLevel(logging.INFO)

def spawn_bot(channel, limit):
	chat = WS_IRC(channel, limit)
	chat.start()


def sem_val(sem):
	return int(str(sem).split("=")[1].split(")")[0])

if __name__ == "__main__":
	if platform.system() == "Windows":
		multiprocessing.freeze_support()

	limit = multiprocessing.Semaphore(config.BURST_RATE_30)
	processes = []

	def end_clean(num, frame):
		for p in processes:
			p.terminate()
		for p in processes:
			p.join()
		exit()

	signal.signal(signal.SIGINT, end_clean)

	for c in config.CHANNELS:
		p = multiprocessing.Process(target=spawn_bot, args=(c, limit))
		processes.append(p)

	for p in processes:
		p.start()

	while True:
		time.sleep(30)
		logging.debug(sem_val(limit))
		while sem_val(limit) < config.BURST_RATE_30:
			limit.release()
