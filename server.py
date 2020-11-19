import http.server
import socketserver
import json
import pandas as pd
import numpy as np
import argparse

def get_lyrics_json():
    df = pd.read_csv('preprocessing/Will Smith Just the Two of Us merged.csv')
    df = normalize_positivity(df)
    return json.dumps(df.to_dict('records'))

def normalize_positivity(df):
    # Get the line positivity.
    # 1.0 if line_score is 1 and label is Positive.
    # -1.0 if linescore is 1.0 and label is Negative
    df['line_positivity'] = np.where(df['line_label'] == 'POSITIVE', df['line_score'], -1.*df['line_score'])

    # Sort, rank, then normalize to get a uniform distribution of line positivities 0-1.0
    line_positivities_sorted = sorted(df['line_positivity'].unique())
    df['line_positivity_rank'] = df['line_positivity'].apply(lambda positivity : line_positivities_sorted.index(positivity))
    df['line_positivity_norm'] = df['line_positivity_rank'] / df['line_positivity_rank'].max()

    # Get the word positivity.
    # 1.0 if hugface_score is 1 and label is Positive.
    # -1.0 if hugface_score is 1.0 and label is Negative
    df['word_positivity'] = np.where(df['hugface_label'] == 'POSITIVE', df['hugface_score'], -1.*df['hugface_score'])

    # Sort, rank, then normalize to get a uniform distribution of line positivities 0-1.0
    word_positivities_sorted = sorted(df['word_positivity'].unique())
    df['word_positivity_rank'] = df['word_positivity'].apply(lambda positivity : word_positivities_sorted.index(positivity))
    df['word_positivity_norm'] = df['word_positivity_rank'] / df['word_positivity_rank'].max()
    return df

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
            self._set_headers()
            self.wfile.write(get_lyrics_json().encode())
            return
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

parser = argparse.ArgumentParser(description='Server Parameters')
parser.add_argument('--port', type=int, default=8081, help='sum the integers (default: find the max)')

args = parser.parse_args()

Handler = MyRequestHandler

with socketserver.TCPServer(("", args.port), Handler) as httpd:
    print("serving at port", args.port)
    httpd.serve_forever()