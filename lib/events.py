from pprint import pprint

_eventListeners = {}


def _addListenerFor(listener, event_type):
    if(not event_type in _eventListeners):
        _eventListeners[event_type] = []
    _eventListeners[event_type].append(listener)


def addListener(listener, event_type="_all"):
    if(isinstance(event_type, list)):
        for i in event_type:
            _addListenerFor(listener, i)
    else:
        _addListenerFor(listener, event_type)


def trigger(event_type, event_dict={}):
    for listener in _eventListeners.get("_all", []):
        try:
            getattr(listener, "processEvent")(event_type, event_dict)
        except Exception as e:
            print("Error propagating event %s (%s) : %s" % (event_type, event_dict, e))

    for listener in _eventListeners.get(event_type, []):
        try:
            getattr(listener, "processEvent")(event_type, event_dict)
        except Exception as e:
            print("Error propagating event %s (%s) : %s" % (event_type, event_dict, e))
