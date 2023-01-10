from bot import bot
import telebot
import flask
import os
from controllers.spotify_controller import Spotify_controller
import requests
import json


app = flask.Flask(__name__)

TOKEN = os.getenv('TOKEN')
URL = os.getenv('URL')
WEBHOOK_URL_PATH = '/updates/'
WEBHOOK_URL = 'https://api.telegram.org/bot%s/setWebhook?url=%s' % (
    TOKEN,
    URL+WEBHOOK_URL_PATH
    )
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
AMPLITUDE_API_KEY = os.getenv('AMPLITUDE_API')
sp = Spotify_controller(CLIENT_ID, CLIENT_SECRET)


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    bot.remove_webhook()
    s = bot.set_webhook(WEBHOOK_URL)
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return '<h1>Hello there</h1>'


@bot.message_handler(commands=['start', 'help'])
def send_command_message(message):
    msg = '''
This bot can help you find and share music on Spotify.
It works automatically, no need to add it anywhere.
Simply open any of your chats and type

@spotiSearchBot something

in the message field.
Then tap on a result to send.
For example, try typing @spotiSearchBot Gangnam Style here.
You can search both by track and by artist '''
    bot.reply_to(message, msg)


@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_text(inline_query):
    amp_event = {
        "user_id": inline_query.from_user.id,  # unique user identifier
        "event_type": "inline_search_event",  # the name of event
        "user_properties": {
            "language_code": inline_query.from_user.language_code
        },
        "event_properties": {
            "query": inline_query.query
        }
    }
    AMPLITUDE_ENDPOINT = "https://api.amplitude.com/2/httpapi"
    _ = requests.post(AMPLITUDE_ENDPOINT, data=json.dumps(
        {
            'api_key': AMPLITUDE_API_KEY,
            'events': [amp_event],
            }
        )
                        )
    bot.answer_inline_query(
        inline_query.id,
        sp.get_iq_articles(inline_query.query)
    )
