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
        self.replace_generic_banner('SB')
        return
        if not self.user.get_replaced_generic_banner():
            behaviour = self.client_data.check_behaviour(self.user)
            if behaviour is not None:
                print(f'== Calculated Behaviour = {behaviour}')
                self.user.set_behaviour(behaviour)
                self.replace_generic_banner(behaviour)

        # save updates to user
        print('Save User: ', self.user.save_user())

    def replace_generic_banner(self, assumed_behaviour):
        html = self.client_data.calc_banner(assumed_behaviour)
        command_sender.push_banner_to_user(self.client, self.uuid, str(html))
        self.user.set_replaced_generic_banner()
