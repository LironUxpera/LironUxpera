from user import User
from send_command import SendCommand

command_sender = SendCommand()


class UserSession:
    def __init__(self, client, uuid, client_data):
        self.client = client
        self.uuid = uuid
        self.client_data = client_data

        self.user = User(self.client, self.uuid)

    def add_event(self, event):
        print('UserSession Add event')
        self.user.add_event(event)
        if not self.user.get_replaced_generic_banner():
            behaviour = self.check_behaviour()
            if behaviour:
                print(f'== Behaviour={behaviour}')
                self.user.set_behaviour(behaviour)
                self.replace_generic_banner(behaviour)

        # save updates to user
        print('Save User: ', self.user.save_user())

    def check_behaviour(self):
        print('$$$$$')
        print('Checking behaviour 1')
        session_start_time = self.user.get_session_start_time()
        events = self.user.get_events()
        behaviour = self.user.get_behaviour()
        if not events:
            return behaviour

        print('Checking behaviour 2')
        last_event = events[-1]
        last_time = last_event.time - session_start_time
        last_type = last_event.event_type
        print(f'== Checking time={last_time} event={last_type}')

        calculated_behavior = self.client_data.check_behaviour(last_time, last_type)

        if calculated_behavior is not None:
            behaviour = calculated_behavior

        return behaviour

    def replace_generic_banner(self, assumed_behaviour):
        html = self.client_data.calc_banner(assumed_behaviour)
        command_sender.push_banner_to_user(self.client, self.uuid, str(html))
        self.user.set_replaced_generic_banner()
