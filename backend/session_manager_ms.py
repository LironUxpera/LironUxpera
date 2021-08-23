import json
from bottle import Bottle, request
from event import Event

app = Bottle()


@app.get("/hello")
def hello():
    return "Hello World!"


@app.post("/event")
def event():
    record = request.json

    print(json.dumps(record, indent=2))

    event_obj = Event()
    event_obj.parse(record)
    event_obj.save_event()

    return "OK"


print('Bottle API MicroService ready')

app.run(port=8080)
