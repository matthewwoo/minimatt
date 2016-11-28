import httplib2
from googleapiclient import discovery
from oauth2client import client
import flask
from flask import Flask, request
from src import medium
from src.models.calendar import Calendar
import json

app = Flask(__name__)
app.secret_key = 'super secret key'

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = '/Users/mattw/Dropbox/Programming/MiniWooBot/client_secret.json'

@app.route('/')
def home():
    return "<p>Running</p>"

@app.route('/slots')
def slots():
    print request.remote_user
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http_auth)
        cal = Calendar()
        today = cal.date_range()
        busy_slots = cal.busy_slots(service=service, body=today)
        slots = cal.potential_slot()
        free_slots = []
        i = 0
        while i <= 1:
            if cal.check_slot(slots[i], busy_slots):
                i += 1
            free_slots.append(slots[i])
            i += 1
        json_slots = cal.post_dates(free_slots)
        return flask.jsonify(json_slots)

@app.route('/oauth2callback')
def oauth2callback():
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
        scope=SCOPES,
        redirect_uri=flask.url_for('oauth2callback', _external=True))
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('slots'))


@app.route('/posts', methods=['GET'])
def posts():
    posts = medium.get_posts(3)
    return flask.jsonify(posts)


@app.route('/test', methods=['GET'])
def test():
    x = {"messages": [{"text": "Welcome to our store!"},{"text": "How can I help you?"}]}
    return flask.jsonify(x)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
