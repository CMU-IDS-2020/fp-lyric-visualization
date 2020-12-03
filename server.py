import http.server
import socketserver
import json
import os
import pandas as pd
import numpy as np
import argparse
from urllib.parse import urlparse, parse_qs

from preprocessing.lyrics_preprocess import preprocess_lyrics
from preprocessing.dict_preprocess import preprocess_dict
from preprocessing.merge_dataframes import merge_dataframes
from preprocessing.tsne import tsne_list

import lyricsgenius
genius = lyricsgenius.Genius("tub_dvzlNtK1D1lLS7o4YUqX2fGBnJdAVbW_OgjEjRKtfhyUopjvonY50UzhPlKe")

CACHE_DIR = 'cache'

def get_lyrics_df(artist_name, song_name):
    # Get genius results in case the user did not type something correctly.
    # Helps with consistency in file names.
    song = genius.search_song(song_name, artist_name)
    song_name, artist_name = song.title, song.artist

    lyrics_fn = os.path.join(CACHE_DIR, artist_name + " " + song_name + " lyrics.csv")
    lines_fn = os.path.join(CACHE_DIR, artist_name + " " + song_name + " lines.csv")

    if os.path.exists(lyrics_fn):
        # Used cached file
        lyrics_df = pd.read_csv(lyrics_fn, encoding="utf-8")
        lines_df = pd.read_csv(lines_fn, encoding="utf-8")
    else:
        # Start from scratch
        lyrics_df, lines_df = preprocess_lyrics(artist_name, song_name)
        dict_df = preprocess_dict(lyrics_df)
        lyrics_df, lines_df = merge_dataframes(lyrics_df, lines_df, dict_df)

        # Cache the file
        lyrics_df.to_csv(lyrics_fn, encoding="utf-8")
        lines_df.to_csv(lines_fn, encoding="utf-8")

    return lyrics_df, lines_df


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

            lyrics_df0, lines_df0 = get_lyrics_df(artist_name0, song_name0)
            lyrics_df1, lines_df1 = get_lyrics_df(artist_name1, song_name1)

            # Do the tsne for the words combined
            all_words_unique = list(set(list(lyrics_df0['word_can_search'].unique()) + list(lyrics_df1['word_can_search'].unique())))
            tsne_dict = tsne_list(all_words_unique)
            lyrics_df0['tsne_x_combined'] = lyrics_df0['word_can_search'].apply(lambda x: tsne_dict[x][0])
            lyrics_df0['tsne_y_combined'] = lyrics_df0['word_can_search'].apply(lambda x: tsne_dict[x][1])
            lyrics_df1['tsne_x_combined'] = lyrics_df1['word_can_search'].apply(lambda x: tsne_dict[x][0])
            lyrics_df1['tsne_y_combined'] = lyrics_df1['word_can_search'].apply(lambda x: tsne_dict[x][1])

            # Do the tsne for the words combined
            all_lines_unique = list(set(list(lines_df0['line_classified'].unique()) + list(lines_df1['line_classified'].unique())))
            tsne_dict = tsne_list(all_lines_unique)
            lines_df0['tsne_x_combined'] = lines_df0['line_classified'].apply(lambda x: tsne_dict[x][0])
            lines_df0['tsne_y_combined'] = lines_df0['line_classified'].apply(lambda x: tsne_dict[x][1])
            lines_df1['tsne_x_combined'] = lines_df1['line_classified'].apply(lambda x: tsne_dict[x][0])
            lines_df1['tsne_y_combined'] = lines_df1['line_classified'].apply(lambda x: tsne_dict[x][1])

            # Convert to dictionaries
            lyrics0, lyrics1, lines0, lines1 = lyrics_df0.to_dict('records'), lyrics_df1.to_dict('records'), \
                    lines_df0.to_dict('records'), lines_df1.to_dict('records')

            output_json = json.dumps({'lyrics0' : lyrics0, 'lines0' : lines0, 'lyrics1': lyrics1, 'lines1': lines1})

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