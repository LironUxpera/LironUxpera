import json
  from bottle import Bottle, response, HTTPResponse, request
  from pymongo import MongoClient

  app = Bottle()

  @app.get("/hello")
  def hello():
      return "Hello World!"


  @app.post("/event")
  def event():
      record = request.json

      print(json.dumps(record, indent=2))

      save_event(record)

      return  "OK"


  def save_event(record):
      """creates in mongo event record"""

      client = record["messageAttributes"]["Client"]["stringValue"]
      uuid = record["messageAttributes"]["UUID"]["stringValue"]
      type = record["messageAttributes"]["Type"]["stringValue"]
      body = record["body"]

      event = {
          'client': client,
          'uuid': uuid,
          'type': type,
          'body': body,
      }
      return events.insert_one(event)


  client = MongoClient()
  db = client.uxpera
  events = db.events

  print('Bottle API MicroService ready')

  # run()
  app.run(port=8080)

