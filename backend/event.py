# event class

import json
from pymongo import MongoClient


mongo_client = MongoClient()


class Event:
    def __init__(self):
        self.client = ''
        self.uuid = ''
        self.event_type = ''
        self.time = 0
        self.body = None

    def __str__(self):
        return f'Client: {self.client}\n' \
               f'UUID: {self.uuid}\n' \
               f'Type: {self.event_type}\n' \
               f'Time: {self.time}\n' \
               f'Body: {self.body}\n'

    def parse(self, msg_record):
        self.client = msg_record["messageAttributes"]["Client"]["stringValue"]
        self.uuid = msg_record["messageAttributes"]["UUID"]["stringValue"]
        self.event_type = msg_record["messageAttributes"]["Type"]["stringValue"]
        self.time = int(msg_record["messageAttributes"]["Time"]["stringValue"])
        self.body = json.loads(msg_record["body"])

        # fix amir's event names for links
        if self.event_type == 'link' and 'title' in self.body:
            print('*** link with title')
            title = self.body['title']
            if title == 'Terms And Conditions':
                self.event_type = 'terms_and_cond'
            elif title == 'Security and Privacy':
                self.event_type = 'security_and_priv'
            elif title == 'About us':
                self.event_type = 'about_us'
            elif title == 'New Arrivals':
                self.event_type = 'new_arrivals'
            elif title == 'Best Sellers':
                self.event_type = 'best_sellers'
            elif title == 'Promotions':
                self.event_type = 'promotions'
            elif title == 'Reviews':
                self.event_type = 'reviews'
        else:
            print('*** NOT link with title')

    def save_event(self):
        """save event to mongo"""

        event_obj = {
            'client': self.client,
            'uuid': self.uuid,
            'type': self.event_type,
            'time': self.time,
            'body': self.body,
        }
        mongo_client.uxpera.events.insert_one(event_obj)
