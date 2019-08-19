import spotipy
import random
from spotipy.oauth2 import SpotifyClientCredentials

import global_vars


# Spotify credentials
# client_id = global_vars.SPOTIFY_ID
# client_secret = global_vars.SPOTIFY_SECRET

def random_song():
    # random song generator from aeiou and spotify ids/secret

    client_credentials_manager = SpotifyClientCredentials(client_id=global_vars.SPOTIFY_ID,
                                                          client_secret=global_vars.SPOTIFY_SECRET)
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    r_list = ['a','e','i','o','u']
    r_char = random.choice(r_list)

    r_offset = random.randint(1,1000)

    # get 1 random song from spotify
    results = spotify.search(q=r_char, type='track', offset=r_offset, limit=1)
    artist = results['tracks']['items'][0]['artists'][0]['name']
    song_name = results['tracks']['items'][0]['name']
    # print(results)

    return artist, song_name



# items = results['tracks']['items'][0]['name]
# if len(items) > 0:
#     artist = items[0]
#     print(artist['name'], artist['images'][0]['url'])
