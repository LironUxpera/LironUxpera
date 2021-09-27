# event class

# import json
from pymongo import MongoClient


mongo_client = MongoClient()


class User:
    def __init__(self, client, uuid):
        self.client = client
        self.uuid = uuid

    # def __str__(self):
    #     return f'Client: {self.client}\n' \
    #            f'UUID: {self.uuid}\n' \
    #            f'Type: {self.event_type}\n' \
    #            f'Time: {self.time}\n' \
    #            f'Body: {self.body}\n'

    def save_user(self):
        """save user to mongo"""

        user_obj = {
            'client': self.client,
            'uuid': self.uuid,
        }
        # TODO handle update of user
        mongo_client.uxpera.users.insert_one(user_obj)
