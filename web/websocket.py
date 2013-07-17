# coding: utf-8
import json


def handle_websocket(ws, user_id):
    print 'new guy :)'
    while True:
        message = ws.receive()
        if message is None:
            break
        message = json.loads(message)
        ws.send(json.dumps({'output': message['output']}))
        print user_id
