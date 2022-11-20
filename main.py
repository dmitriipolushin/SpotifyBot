import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import json
from bot import bot
import telebot
import flask
import requests
import os


app = flask.Flask(__name__)

TOKEN = os.getenv('TOKEN')
URL = os.getenv('URL')
WEBHOOK_URL_PATH = '/updates/'
WEBHOOK_URL = 'https://api.telegram.org/bot%s/setWebhook?url=%s' % (TOKEN, URL+WEBHOOK_URL_PATH)
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

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
        print(s)
        return "webhook setup ok" 
    else: 
        return "webhook setup failed" 

@app.route('/') 
def index(): 
    return '<h1>Hello there</h1>'


def get_information(item):
    info = {}
    album = item['album']
    info['album_url'] = album['external_urls']['spotify']
    info['album_img'] = album['images'][2]['url']
    artists = item['artists']
    info['artist'] = {
        'name': album['artists'][0]['name'],
        'link': album['artists'][0]['external_urls']['spotify'],
    }
    info['to_listen'] = item['external_urls']['spotify']
    info['id'] = item['id']
    info['name'] = sp.track(info['id'])['name']
    return info

cid = CLIENT_ID
secret = CLIENT_SECRET


client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


@bot.message_handler(commands=['start', 'help'])
def send_command_message(message):
    chat_id = message.chat.id
    msg = '''
    This bot can help you find and share music on Spotify. 
It works automatically, no need to add it anywhere. 
Simply open any of your chats and type @spotiSearchBot something in the message field. 
Then tap on a result to send.
For example, try typing @spotiSearchBot Gangnam Style here.
You can search both by track and by artist '''
    bot.reply_to(message, msg)


@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_text(inline_query):  
    bot.answer_inline_query(  
        inline_query.id,  
        get_iq_articles(inline_query.query)  
    )


def get_iq_articles(query):
    try:
        
        # type_of_search, req = query.split(' ')[0], query.split(' ')[1:]
        
        results = sp.search(q=query, type=['track', 'artist'], limit=10)

        info = []
        for item in results['tracks']['items']:
            info.append(get_information(item))
        
        result = []
        cnt = 0
        desc_msg = 'Tap to get link to track'
        # [inline URL](http://www.example.com/)
        out_msg = '[Listen track on Spotify]({})\nName of the track: *{}*\nArtist: *{}*\n[Link to the artist]({})\n[Link to the album]({})'
        for item in info:
            title = item['artist']['name'] + ' - ' + item['name']
            result.append(
                telebot.types.InlineQueryResultArticle(id=str(cnt),
                                               title=title, 
                                               description=desc_msg,
                                               input_message_content=telebot.types.InputTextMessageContent(
                                                   out_msg.format(
                                                       item['to_listen'],
                                                       item['name'],
                                                       item['artist']['name'],
                                                       item['artist']['link'],
                                                       item['album_url']
                                                       ),
                                                   parse_mode='Markdown',
                                                   ),
                                               thumb_url=item['album_img']
                                               )   
                )
            cnt += 1
        return result
            
            
    except IndexError as e:
        return


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
