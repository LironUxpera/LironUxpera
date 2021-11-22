from demo_client_data import DemoClientData
from premier_staging_client_data import PremierStagingClientData
from premier_client_data import PremierClientData
from livia_client_data import LiviaClientData
from user_session import UserSession


class SessionManager:
    def __init__(self):
        self.clients_data = {}
        self.clients = {}  # user_sessions accessed via client key and then uuid key
        self.user_sessions = []  # same user_sessions as above as FIFO list for memory management
        self.max_sessions = 2000
        self.reduce_sessions = 500

        # TODO this list should probably be in csv or simply read all folders under client
        # TODO for now we will hard code the list
        # client_data = DemoClientData()
        # self.clients_data[client_data.client] = client_data

        client_data = PremierClientData()
        self.clients_data[client_data.client] = client_data

        client_data = PremierStagingClientData()
        self.clients_data[client_data.client] = client_data

        # client_data = LiviaClientData()
        # self.clients_data[client_data.client] = client_data

    def add_event(self, event):
        if event.client not in self.clients_data.keys():
            print(f'ERROR: event with unknown client "{event.client}"')
            return

        client_data = self.clients_data[event.client]

        print('SM Add event')

        # if don't have this client yet then create new entry for it
        if event.client not in self.clients.keys():
            print('SM Add event - CASE 1')
            user_session = UserSession(event.client, event.uuid, client_data)
            self.clients[event.client] = {event.uuid: user_session}
            self.user_sessions.append(user_session)

        client = self.clients[event.client]

        # if don't have this uuid yet then create new entry for it
        if event.uuid not in client.keys():
            print('SM Add event - CASE 2')
            user_session = UserSession(event.client, event.uuid, client_data)
            client[event.uuid] = user_session
            self.user_sessions.append(user_session)

        user_session = client[event.uuid]

        # add the event to the user session
        user_session.add_event(event)

        # code to limit the number of open sessions
        if len(self.user_sessions) > self.max_sessions:
            for _ in range(self.reduce_sessions):
                user_session = self.user_sessions.pop(0)
                del self.clients[user_session.client][user_session.uuid]

            # additional code to remove by stale time - 4 hours
            done_with_stales = False
            while not done_with_stales and len(self.user_sessions) > 0:
                user_session = self.user_sessions[0]
                stale = user_session.user.user_not_accessed_for_x_hours_ago(4)
                if stale:
                    user_session = self.user_sessions.pop(0)
                    del self.clients[user_session.client][user_session.uuid]
                else:
                    done_with_stales = True

