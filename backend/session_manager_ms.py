import json
from bottle import Bottle, request
from event import Event
from session_manager import SessionManager

app = Bottle()
session_mgr = SessionManager()


# TODO think of some way to monitor this service, load on memory and mongo, and disk

@app.get("/hello")
def hello():
    return "Hello World!"


@app.post("/event")
def event():
    record = request.json

    # print(json.dumps(record, indent=2))

    # parse event
    event_obj = Event()
    event_obj.parse(record)
    print()
    print(event_obj)
    print()

    # update session manager with event
    session_mgr.add_event(event_obj)

    # save event to events table
    event_obj.save_event()

    return "OK"


print('Bottle API MicroService ready')

app.run(port=8080)
