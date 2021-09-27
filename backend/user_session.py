from send_command import SendCommand

command_sender = SendCommand()


class UserSession:
    def __init__(self, client, uuid, client_data):
        self.client = client
        self.uuid = uuid
        self.client_data = client_data

        # TODO save user meta data
        # TODO add user persistent data
        # TODO handle sessions
        self.assumed_behaviour = ''  # DP,SL, NBS, BH, SB
        self.replaced_generic_banner = False
        self.events = []

    def add_event(self, event):
        print('User Add event')
        self.events.append(event)
        if not self.replaced_generic_banner:
            behavior = self.check_behaviour()
            if behavior:
                print(f'== Behaviour={behavior}')
                self.assumed_behaviour = behavior
                self.replace_generic_banner(behavior)

    def check_behaviour(self):
        behaviour = ''
        if not self.events:
            return behaviour

        last_event = self.events[-1]
        last_time = last_event.time
        last_type = last_event.event_type
        print(f'== Checking time={last_time} event={last_type}')

        # left check for events in first 5 seconds
        if last_time <= 5000:
            if last_type in self.client_data.dp_events:
                behaviour = 'DP'
            elif last_type in self.client_data.bh_events:
                behaviour = 'BH'
            elif last_type in self.client_data.nb_events:
                behaviour = 'NBS'
            elif last_type in self.client_data.sl_events:
                behaviour = 'SL'
            elif last_type in self.client_data.sb_events:
                behaviour = 'SB'
        elif last_time <= 15000:
            if last_type in self.client_data.sb_events:
                behaviour = 'SB'

        return behaviour

    def replace_generic_banner(self, assumed_behaviour):
        html = self.client_data.calc_banner(assumed_behaviour)
        command_sender.push_banner_to_user(self.client, self.uuid, str(html))
        self.replaced_generic_banner = True
