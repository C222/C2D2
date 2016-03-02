CREATE KEYSPACE IF NOT EXISTS c2d2 WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

USE c2d2;

/*DROP TABLE IF EXISTS chat;
DROP TABLE IF EXISTS bans;*/

CREATE TABLE IF NOT EXISTS chat (
	nick text,
	channel text,
	utc timestamp,
	tags map<text, text>,
	chat text,
	link list<text>,
	PRIMARY KEY ((nick, channel), utc)
);

CREATE TABLE IF NOT EXISTS bans (
	nick text,
	channel text,
	utc timestamp,
	PRIMARY KEY ((nick, channel), utc)
);