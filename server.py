import http.server
import socketserver
import json
import os
import string
import pandas as pd
import numpy as np
import argparse
from urllib.parse import urlparse, parse_qs

from preprocessing.lyrics_preprocess import preprocess_lyrics
from preprocessing.dict_preprocess import preprocess_dict
from preprocessing.merge_dataframes import merge_dataframes, positivity_barplot_data
from preprocessing.tsne import tsne_list

from spotify_embedding import get_spotify_embedding

import lyricsgenius
genius = lyricsgenius.Genius("tub_dvzlNtK1D1lLS7o4YUqX2fGBnJdAVbW_OgjEjRKtfhyUopjvonY50UzhPlKe")

CACHE_DIR = 'cache'
HAND_PICKED_EXAMPLE_CACHE = 'hand_picked_example_cache'

if not os.path.exists(CACHE_DIR): os.mkdir(CACHE_DIR)
if not os.path.exists(HAND_PICKED_EXAMPLE_CACHE): os.mkdir(HAND_PICKED_EXAMPLE_CACHE)

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

def get_lyrics_df(artist_name, song_name, isHandPickedExample):
    lyrics_fn = os.path.join(HAND_PICKED_EXAMPLE_CACHE if isHandPickedExample else CACHE_DIR,
                             format_filename(artist_name + " " + song_name + " lyrics.csv"))
    lines_fn = os.path.join(HAND_PICKED_EXAMPLE_CACHE if isHandPickedExample else CACHE_DIR,
                            format_filename(artist_name + " " + song_name + " lines.csv"))

    if os.path.exists(lyrics_fn):
        # Used cached file
        print('Using a cached file for the song: ', song_name)
        lyrics_df = pd.read_csv(lyrics_fn, encoding="utf-8")
        lines_df = pd.read_csv(lines_fn, encoding="utf-8")
    else:
        # Start from scratch
        lyrics_df, lines_df = preprocess_lyrics(artist_name, song_name)
        dict_df = preprocess_dict(lyrics_df)
        lyrics_df, lines_df = merge_dataframes(lyrics_df, lines_df, dict_df)

        # Adding song name and artist name to the df
        lyrics_df['song_name'] = song_name
        lines_df['song_name'] = song_name
        lyrics_df['artist_name'] = artist_name
        lines_df['artist_name'] = artist_name

        # Cache the file
        lyrics_df.to_csv(lyrics_fn, encoding="utf-8")
        lines_df.to_csv(lines_fn, encoding="utf-8")


    return lyrics_df, lines_df, lyrics_fn, lines_fn

def compute_tsne(df0, df1, column):
    ''' Compute t-SNE using a specified column from two different data frames
        Alters the dataframes directly, no need to return them'''
    all_values_unique = list(set(list(df0[column].unique()) + list(df1[column].unique())))
    tsne_dict = tsne_list(all_values_unique)
    df0['tsne_x_combined'] = df0[column].apply(lambda x: tsne_dict[x][0])
    df0['tsne_y_combined'] = df0[column].apply(lambda x: tsne_dict[x][1])
    df1['tsne_x_combined'] = df1[column].apply(lambda x: tsne_dict[x][0])
    df1['tsne_y_combined'] = df1[column].apply(lambda x: tsne_dict[x][1])


class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        possible_name = self.path.strip("/")+'.html'
        if self.path == '/':
            self.path = '/index.html'
        elif self.path.startswith('/getSong'):
            query = urlparse(self.path).query
            query_components = parse_qs(query)

            artist_name0, song_name0 = query_components["artist0"][0].lower().strip(), query_components["songName0"][0].lower().strip()
            artist_name1, song_name1 = query_components["artist1"][0].lower().strip(), query_components["songName1"][0].lower().strip()

            # Get genius results in case the user did not type something correctly.
            # Helps with consistency in file names.
            song = genius.search_song(song_name0, artist_name0)
            song_name0, artist_name0 = song.title, song.artist
            song = genius.search_song(song_name1, artist_name1)
            song_name1, artist_name1 = song.title, song.artist

            # Check if this is a pre-selected pairing of songs. If so, we might be able to avoid computing t-SNE
            isHandPickedExample = query_components["isHandPickedExample"][0].lower().strip() == 'true'

            lyrics_df0, lines_df0, lyrics_fn0, lines_fn0 = get_lyrics_df(artist_name0, song_name0, isHandPickedExample)
            lyrics_df1, lines_df1, lyrics_fn1, lines_fn1 = get_lyrics_df(artist_name1, song_name1, isHandPickedExample)

            # Positivity Barplot data
            pos_barplot_data = positivity_barplot_data(lyrics_df0, lyrics_df1)

            if isHandPickedExample and ('tsne_x_combined' in lyrics_df0.columns) and ('tsne_x_combined' in lyrics_df1.columns):
                # Don't need to do anything, cached file is good to go
                print('Using cached version of a pre-selected example as is. No need to compute t-SNE.')
            else:
                # Compute t-SNE because it wasn't saved for this song comparison combination
                # Do the tsne for the words combined
                print('Computing t-SNE.')
                compute_tsne(lyrics_df0, lyrics_df1, 'word_can_search')

                # Do the tsne for the words combined
                compute_tsne(lines_df0, lines_df1, 'line_classified')

            if isHandPickedExample:
                # Save this pre-selected pairing again to save the t-SNE values
                lyrics_df0.to_csv(lyrics_fn0, encoding="utf-8")
                lines_df0.to_csv(lines_fn0, encoding="utf-8")
                lyrics_df1.to_csv(lyrics_fn1, encoding="utf-8")
                lines_df1.to_csv(lines_fn1, encoding="utf-8")

            # Convert to dictionaries
            lyrics0, lyrics1, lines0, lines1 = lyrics_df0.to_dict('records'), lyrics_df1.to_dict('records'), \
                    lines_df0.to_dict('records'), lines_df1.to_dict('records')

            output_json = json.dumps({
                    'lyrics0' : lyrics0,
                    'lines0' : lines0,
                    'lyrics1': lyrics1,
                    'lines1': lines1,
                    'pos_barplot_data': pos_barplot_data,
                    'song0_html_embedding': get_spotify_embedding(song_name0, artist_name0),
                    'song1_html_embedding': get_spotify_embedding(song_name1, artist_name1)})

            self._set_headers()
            self.wfile.write(output_json.encode())
            return
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

parser = argparse.ArgumentParser(description='Server Parameters')
parser.add_argument('--port', type=int, default=8081, help='sum the integers (default: find the max)')

args = parser.parse_args()

Handler = MyRequestHandler

with socketserver.TCPServer(("", args.port), Handler) as httpd:
    print("serving at port", args.port)
    httpd.serve_forever()