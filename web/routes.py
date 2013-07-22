# coding: utf-8
from web import app
from flask import render_template


@app.route('/')
def index():
    return render_template('index.html')
