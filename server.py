import http.server
import socketserver
import json
import pandas as pd
import numpy as np
import argparse


def get_lyrics_json():
    df = pd.read_csv('preprocessing/Will Smith Just the Two of Us merged.csv')
    return json.dumps(df.to_dict('records'))


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