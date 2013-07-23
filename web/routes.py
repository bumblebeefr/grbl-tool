# coding: utf-8
from web import app, grbl, macros
from flask import render_template, request, Response
import simplejson as json


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/command.json')
def command():
    command = request.args.get('cmd', '')
    return Response(
        response=json.dumps(
        grbl.processCommand(macros, command)),
        status=200,
        content_type='application/json')
