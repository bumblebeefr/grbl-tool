# coding: utf-8
import os

from flask import Flask
from flask import session
from flask import request
from websocket import handle_websocket
from pprint import pprint

app = Flask(__name__)
app.secret_key = 'sdhfsf!gqs!y65g?hjg56743GHghjgjkgf*708!HFFjgqsdgh%+/hoih'
app.debug = True


def webapp(environ, start_response):
    path = environ["PATH_INFO"]
    # pprint(environ)
    if path == "/websocket":
        with app.request_context(environ):
            user_id = None
            user_id = session.get('user_id', None)
            handle_websocket(environ["wsgi.websocket"], user_id)
    else:
        return app(environ, start_response)


import routes
