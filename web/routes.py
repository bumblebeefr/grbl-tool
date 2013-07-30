# coding: utf-8
from flask import render_template, request, Response
from web import app, grbl, macros
import simplejson as json
import time


startup_timetamp = time.time()


@app.route('/')
def index():
    return render_template('index.html', v=startup_timetamp)


@app.route('/command.json')
def command():
    command = request.args.get('cmd', '')
    return Response(
        response=json.dumps(
        grbl.processCommand(macros, command)),
        status=200,
        content_type='application/json')
