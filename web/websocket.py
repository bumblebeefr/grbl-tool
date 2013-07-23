# coding: utf-8
import simplejson as json

_connected = False


def handle_websocket(ws, grbl):
    global _connected
    if _connected:
        ws.send(json.dumps({"welcome": False}))
    else:
        _connected = True
        ws.send(json.dumps({"welcome": True}))
        while True:
            message = ws.receive()
            if message is None:
                break
            message = json.loads(message)
            ws.send(json.dumps({'output': message['output']}))
