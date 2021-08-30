from user_session import UserSession


class SessionManager:
    def __init__(self):
        self.clients = {}

    def add_event(self, event):
        # if don't have this client yet then create new entry for it
        if event.client not in self.clients.keys():
            self.clients[event.client] = {event.uuid: UserSession(event.client, event.uuid)}

        client = self.clients[event.client]

        # if don't have this uuid yet then create new entry for it
        if event.uuid not in client.keys():
            client[event.uuid] = UserSession(event.client, event.uuid)

        user_session = client[event.uuid]

        # add the event to the user session
        user_session.add_event(event)
