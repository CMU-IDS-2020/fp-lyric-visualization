import os
import string

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

SPOTIFY_EMBEDDING_CACHE_DIR = 'spotify_embedding_cache'
if not os.path.exists(SPOTIFY_EMBEDDING_CACHE_DIR): os.mkdir(SPOTIFY_EMBEDDING_CACHE_DIR)

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="8e78672ecefa44e58dd8a0b1af9a4fd1",
                                                           client_secret="f48a74f4d6da4312b37f2f7808c08443"))

def format_filename(s):
    """Take a string and return a valid filename constructed from the string.
    Uses a whitelist approach: any characters not present in valid_chars are
    removed. Also spaces are replaced with underscores.

    Note: this method may produce invalid filenames such as ``, `.` or `..`
    When I use this method I prepend a date string like '2009_01_15_19_46_32_'
    and append a file extension like '.txt', so I avoid the potential of using
    an invalid filename.
    FROM: https://gist.github.com/seanh/93666
    """
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ','_') # I don't like spaces in filenames.
    return filename

def get_spotify_embedding(song_name, artist_name):
    html = ''

    # Hand fix for the Step example. Spotify song name is different from Genius.
    if song_name.lower() == 'step (remix)': song_name, artist_name = 'step', 'vampire weekend danny brown'

    cache_fn = os.path.join(SPOTIFY_EMBEDDING_CACHE_DIR, format_filename(artist_name + " " + song_name + ".txt"))

    if os.path.exists(cache_fn):
        # Use the cached version of the embedding
        print('Using cached spotify embedding for', artist_name, song_name)
        f = open(cache_fn, 'r')
        html = f.read()
        f.close()
        return html

    results = sp.search(q='artist:' + artist_name + ' track:' + song_name, limit=1, type='track')

    if results is None or len(results) == 0 or len(results['tracks']['items']) == 0:
        print('Was not able to retrieve results for', artist_name, song_name, 'from spotify.')
    else:
        spotify_track_id = results['tracks']['items'][0]['id']
        html = '<iframe src="https://open.spotify.com/embed/track/' + spotify_track_id + '" ' \
                + '&amp;theme=white&amp;view=coverart" width="300" height="80" frameborder="0" allowtransparency="true"></iframe>'

        # Cache the html
        f = open(cache_fn, "w")
        f.write(html)
        f.close()

    return html
