# coding: utf-8
import os

from flask import Flask
from flask import session
from flask import request
from websocket import handle_websocket
from pprint import pprint
from lib.grbl import Grbl
from lib.macros import Macro

app = Flask(__name__)
app.secret_key = 'sdhfsf!gqs!y65g?hjg56743GHghjgjkgf*708!HFFjgqsdgh%+/hoih'
app.debug = True

grbl = Grbl()
macros = Macro(grbl)


def webapp(environ, start_response):
    path = environ["PATH_INFO"]
    if path == "/websocket":
        with app.request_context(environ):
            handle_websocket(environ["wsgi.websocket"], grbl)
    else:
        return app(environ, start_response)


import routes
