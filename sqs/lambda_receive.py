from __future__ import print_function
import urllib3
import json


def lambda_handler(event, context):
    for record in event['Records']:
        payload = record["body"]
        print(str(payload))
        
        http = urllib3.PoolManager()
        encoded_body = json.dumps(record)
        r = http.request('POST', 'http://54.161.16.58:80/event',
            headers={'Content-Type': 'application/json'},
            body=encoded_body)

