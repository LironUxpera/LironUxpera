from demo_client_data import DemoClientData
from livia_client_data import LiviaClientData
from user_session import UserSession


class SessionManager:
    def __init__(self):
        self.clients = {}
        self.clients_data = {}

        # TODO we need to think if keep everything in memory all the time or we purge from time to time
        # TODO now that we save user info persistently. We should  probably clear users who have old sessions
        # TODO in that case we also need to restore events when we read it back - perhaps unless we are sure it is a new session

        # TODO this list should probably be in csv or simply read all folders under client
        # TODO for now we will hard code the list
        client_data = DemoClientData()
        self.clients_data[client_data.client] = client_data

        client_data = LiviaClientData()
        self.clients_data[client_data.client] = client_data

    def add_event(self, event):
        if event.client not in self.clients_data.keys():
            print(f'ERROR: event with unknown client "{event.client}"')
            return

        client_data = self.clients_data[event.client]

        print('SM Add event')

        # if don't have this client yet then create new entry for it
        if event.client not in self.clients.keys():
            print('SM Add event - CASE 1')
            self.clients[event.client] = {event.uuid: UserSession(event.client, event.uuid, client_data)}

        client = self.clients[event.client]

        # if don't have this uuid yet then create new entry for it
        if event.uuid not in client.keys():
            print('SM Add event - CASE 2')
            client[event.uuid] = UserSession(event.client, event.uuid, client_data)

        user_session = client[event.uuid]

        # add the event to the user session
        user_session.add_event(event)
