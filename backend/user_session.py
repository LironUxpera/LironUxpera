from send_command import SendCommand

command_sender = SendCommand()


class UserSession:
    def __init__(self, client, uuid):
        self.client = client
        self.uuid = uuid

        # TODO save user meta data
        self.assumed_behaviour = ''  # DP,SL, NBS, BH, SB
        self.replaced_generic_banner = False
        self.events = []

    def __str__(self):
        result = ''
        # for client in self.clients.keys():
        #     for uuid in self.clients[client].keys():
        #         user_event
        #         user_str = f'Client: {client}\n' \
        #                    f'UUID: {uuid}\n' \
        #                    f'Type: {self.event_type}\n' \
        #                    f'Time: {self.time}\n' \
        #                    f'Body: {self.body}\n' \
        #                     '===================='
        #         result = result + user_str
        return result

    def add_event(self, event):
        self.events.append(event)
        if not self.replaced_generic_banner:
            behavior = self.check_behaviour()
            if behavior:
                self.assumed_behaviour = behavior
                self.replace_generic_banner()

    def check_behaviour(self):
        behaviour = ''

        # TODO this is very simplistic check, doesn't check first after start and
        if self.events and self.events[-1].event_type == 'search':
            behaviour = 'DP'

        return behaviour

    def replace_generic_banner(self):
        html = f'{self.assumed_behaviour} BANNER'
        command_sender.push_banner_to_user(self.client, self.uuid, html)
