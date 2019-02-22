import requests
from bs4 import BeautifulSoup
from pprint import pprint
import spotipy
import spotipy.util as util


class Track:
    def __init__(self, artist, title):
        self.id = None
        self.artist = artist
        self.title = title

    def get_track_id(self, sp_instance):
        result = sp_instance.search(q='{} {}'.format(self.title, self.artist), type='track', limit=1)
        if result['tracks']['items']:
            self.id = result['tracks']['items'][0]['id']
        else:
            print('Unable to find {} by {}'.format(self.title, self.artist))


class Programme:
    base_url = 'https://www.bbc.co.uk/programmes/'

    def __init__(self, id):
        self.request_url = self.base_url + id
        self.soup = self.make_soup()
        self.dj = self.get_dj()
        self.programme_title = self.get_programme_title()
        self.broadcast_date = self.get_broadcast_date()
        self.tracks = self.get_tracks()
        self.p_id = None

    def make_soup(self):
        r = requests.get(self.request_url)
        if r.status_code != 200:
            print('Oops... Bad response. Please check the programme ID is correct')
            quit()
        s = BeautifulSoup(r.content, features="html.parser")
        return s

    def get_tracks(self):
        track_object_list = []
        track_element = self.soup.find_all('div', class_='segment__track')
        for el in track_element:
            track = el.find_all('span')
            artist = track[0].string
            title = track[1].string
            track_object = Track(artist, title)
            track_object_list.append(track_object)
        return track_object_list

    def get_dj(self):
        dj_el = self.soup.find('div', class_='br-masthead__title')
        dj = dj_el.find('a').string
        return dj

    def get_programme_title(self):
        p_title_el = self.soup.find('div', class_='island')
        p_title = p_title_el.find('h1').string
        return p_title

    def get_broadcast_date(self):
        b_date_el = self.soup.find(id='broadcasts')
        b_date = b_date_el.find('div', class_='broadcast-event__time beta')
        return b_date['content']

    def get_track_ids(self, spotipy_instance):
        for each in self.tracks:
            each.get_track_id(spotipy_instance)

    def create_spotify_playlist(self, spotipy_instance):
        playlist_name = '{} - {}'.format(self.dj, self.programme_title)
        new_playlist = spotipy_instance.user_playlist_create(username, playlist_name)
        self.p_id = new_playlist['id']
        return new_playlist['id']

    def add_tracks_to_spotify_playlist(self, spotipy_instance):
        self.get_track_ids(spotipy_instance)
        pl_id = self.create_spotify_playlist(spotipy_instance)
        t_ids = [track.id for track in self.tracks if track.id is not None]
        spotipy_instance.user_playlist_replace_tracks(username, pl_id, t_ids)


def create_spotipy_instance(username):
    token = util.prompt_for_user_token(username,
                                       'playlist-modify-public user-library-read',
                                       client_id='6efc18b74fc54975a186af04db761e01',
                                       client_secret='fa9766d11abf4f86b47fed01d0e952e0',
                                       redirect_uri='http://localhost:80')
    if token:
        return spotipy.Spotify(auth=token)
    else:
        print("Can't get token for", username)


username = input('Please Enter Your Spotify Username: ')
programme_id = input('Please Enter BBC Programme ID: ')

sp = create_spotipy_instance(username)
p = Programme(programme_id)
p.add_tracks_to_spotify_playlist(sp)

pprint('Playlist Created: https://open.spotify.com/playlist/{}'.format(p.p_id))