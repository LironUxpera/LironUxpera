from user import User
from send_command import SendCommand

command_sender = SendCommand()


class UserSession:
    def __init__(self, client, uuid, client_data):
        self.client = client
        self.uuid = uuid
        self.client_data = client_data

        self.user = User(self.client, self.uuid)

        # TODO handle sessions
        self.replaced_generic_banner = False

    def add_event(self, event):
        print('User Add event')
        self.user.add_event(event)
        if not self.replaced_generic_banner:
            behaviour = self.check_behaviour()
            if behaviour:
                print(f'== Behaviour={behaviour}')
                self.user.set_behaviour(behaviour)
                self.replace_generic_banner(behaviour)

        # save updates to user
        self.user.save_user()

    def check_behaviour(self):
        events = self.user.get_events()
        behaviour = self.user.get_behaviour()
        if not events:
            return behaviour

        last_event = events[-1]
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
