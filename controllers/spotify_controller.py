import telebot
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class Spotify_controller():

    def __init__(self, client_id, client_secret) -> None:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
            )
        self.sp = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager
            )

    def get_information(self, item):
        info = {}
        album = item['album']
        info['album_url'] = album['external_urls']['spotify']
        info['album_img'] = album['images'][2]['url']
        info['artist'] = {
            'name': album['artists'][0]['name'],
            'link': album['artists'][0]['external_urls']['spotify'],
        }
        info['to_listen'] = item['external_urls']['spotify']
        info['id'] = item['id']
        info['name'] = self.sp.track(info['id'])['name']
        return info

    def get_iq_articles(self, query):
        try:

            # type_of_search, req = query.split(' ')[0], query.split(' ')[1:]

            results = self.sp.search(
                q=query,
                type=['track', 'artist'],
                limit=10
                )

            info = []
            for item in results['tracks']['items']:
                info.append(self.get_information(item))

            result = []
            cnt = 0
            desc_msg = 'Tap to get link to track'
            # [inline URL](http://www.example.com/)
            out_msg = '''[Listen track on Spotify]({})
            Name of the track: *{}*
            Artist: *{}*
            [Link to the artist]({})
            [Link to the album]({})'''
            for item in info:
                title = item['artist']['name'] + ' - ' + item['name']
                result.append(
                    telebot.types.InlineQueryResultArticle(
                        id=str(cnt),
                        title=title,
                        description=desc_msg,
                        input_message_content=telebot.types.InputTextMessageContent  # noqa: E501
                        (
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
            return e
