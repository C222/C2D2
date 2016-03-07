import logging
import time
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine.connection import set_session
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns
from cassandra.cqlengine.management import sync_table
from cassandra.query import dict_factory
import os


import config


os.environ['CQLENG_ALLOW_SCHEMA_MANAGEMENT'] = '0'
class MessageModel(Model):
	__table_name__ = "chat"
	__keyspace__ = "c2d2"
	nick = columns.Text(primary_key=True, partition_key=True)
	channel = columns.Text(primary_key=True, partition_key=True)
	utc = columns.DateTime(primary_key=True)
	tags = columns.Map(columns.Text, columns.Text)
	chat = columns.Text()
	link = columns.List(columns.Text)


class CassandraConnection:
	def __init__(self):
		auth_provider = PlainTextAuthProvider(
			username=config.CASSANDRA_USER,
			password=config.CASSANDRA_PASSWORD)
		self.conn = Cluster(config.CASSANDRA_IPS, port=config.CASSANDRA_PORT,
							auth_provider=auth_provider)
		self._started = False
		self.session = None
		self.chat_insert = None
		self.start()

	def start(self):
		self.session = self.conn.connect('c2d2')
		self.session.row_factory = dict_factory
		set_session(self.session)
		sync_table(MessageModel)
		self._started = True

	def on_chat(self, wsirc, msg, hooks):
		if self._started:
			
			if msg.link is not None:
				ln = [str(x) for x in msg.link if x is not None]
			else:
				ln = None
			
			i = MessageModel.create(
			nick=msg.msg['nick'],
			channel=wsirc.channel,
			utc=msg.time,
			tags= msg.tags,
			chat=msg.chat,
			link=ln
			)
			logging.debug(i)

	def distinct(self):
		rows = self.session.execute("SELECT DISTINCT channel, nick FROM chat;")
		return rows
		
	def get_log(self, channel, user, limit=100):
		limit = min(limit, 1000)
		rows = MessageModel.filter(channel=channel, nick=user).order_by("-utc").limit(limit)
		
		result = []
		
		for r in rows:
			result.append(dict(r))
			
		return result
