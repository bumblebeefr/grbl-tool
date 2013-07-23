# coding: utf-8
from Queue import Queue, Empty
import simplejson as json
from time import sleep
import threading
from lib import events

_ws = {}
_message_queue = Queue()


class WSQueueConsumer(threading.Thread):
    def __init__(self):
        super(WSQueueConsumer, self).__init__()
        self.daemon = True
        self.start()

    def run(self):
        while True:
            if("ws" in _ws):
                try:
                    msg = _message_queue.get_nowait()
                    _ws['ws'].send(json.dumps(msg))
                except Empty:
                    sleep(0.01)
                except Exception as e:
    #                 logger.warn("Something goes wrong when getting data from queue : %s", e)
                    sleep(0.01)
            else:
                sleep(1)


def handle_websocket(ws, grbl):
    global _connected
    if("ws" in _ws):
        ws.send(json.dumps({"welcome": False}))
    else:
        ws.send(json.dumps({"welcome": True}))
        _ws['ws'] = ws
        while True:
            message = ws.receive()
            if message is None:
                break
            message = json.loads(message)
            ws.send(json.dumps({'output': message['output']}))
        del(_ws['ws'])


class WsEventListener:
    def processEvent(self, event_type, event_dict):
        print(event_type)
        _message_queue.put({"type": event_type, "data": event_dict})

wsEventListener = WsEventListener()
events.addListener(wsEventListener)

WSQueueConsumer()
