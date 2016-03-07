#!/usr/bin/python2

from flask import Flask, send_from_directory, request, Response
import logging
import json
import config
from functools import wraps

from wsirc import cassandra_connection

cass = None
app = Flask(__name__)

#Basic Auth from: http://flask.pocoo.org/snippets/8/
def check_auth(username, password):
	"""This function is called to check if a username /
	password combination is valid.
	"""
	return username == 'c2d2' and password == config.LOGVIEW_PASSWORD

def authenticate():
	"""Sends a 401 response that enables basic auth"""
	return Response(
	'Could not verify your access level for that URL.\n'
	'You have to login with proper credentials', 401,
	{'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth or not check_auth(auth.username, auth.password):
			return authenticate()
		return f(*args, **kwargs)
	return decorated


@app.route('/')
@requires_auth
def index():
	return send_static("index.html")

@app.route('/api/known')
@requires_auth
def known():
	global cass
	known = {}
	
	for r in cass.distinct():
		if r['channel'] not in known:
			known[r['channel']] = []
		known[r['channel']].append(r['nick'])
	
	return json.dumps(known)

@app.route('/api/log/<channel>/<user>/')
@requires_auth
def log(channel, user):
	global cass
	limit = int(request.args.get('limit', 10))
	return json.dumps(cass.get_log(channel, user, limit), default=lambda x: x.ctime())

@app.route('/static/<path:path>')
@requires_auth
def send_static(path):
	return send_from_directory('static', path)

if __name__ == '__main__':
	cass = cassandra_connection.CassandraConnection()
	cass.start()
	app.run(debug=False, host='0.0.0.0')