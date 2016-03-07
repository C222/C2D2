from flask import Flask, send_from_directory, request
import logging
import json

from wsirc import cassandra_connection

cass = None
app = Flask(__name__)

@app.route('/')
def index():
	return send_static("index.html")

@app.route('/api/known')
def known():
	global cass
	known = {}
	
	for r in cass.distinct():
		if r['channel'] not in known:
			known[r['channel']] = []
		known[r['channel']].append(r['nick'])
	
	return json.dumps(known)

@app.route('/api/log/<channel>/<user>/')
def log(channel, user):
	global cass
	limit = int(request.args.get('limit', 10))
	return json.dumps(cass.get_log(channel, user, limit), default=lambda x: x.ctime())

app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
	cass = cassandra_connection.CassandraConnection()
	cass.start()
	app.run(debug=True)