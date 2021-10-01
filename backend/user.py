# event class

import json
from datetime import datetime, timedelta, timezone
from user_agents import parse
from pymongo import MongoClient


mongo_client = MongoClient()


class User:
    def __init__(self, client, uuid):
        self.client = client
        self.uuid = uuid

        # session info
        self.time = 0
        self.ip = ''
        self.screen_width = None
        self.screen_height = None
        self.time_zone_hours = 0
        self.time_zone_mins = 0
        self.datetime = None
        self.browser = ''
        self.browser_ver = ''
        self.os = ''
        self.os_ver = ''
        self.device = ''
        self.device_brand = ''
        self.device_model = ''
        self.is_mobile = False
        self.is_tablet = False
        self.is_touch_capable = False
        self.is_pc = False
        self.is_bot = False
        self.behaviour = ''

        # global info
        self.first_visit_dt = None  # first visit date
        self.last_visit_dt = None  # last visit date
        self.sessions = 0  # num of sessions

    def __str__(self):
        return f'Client: {self.client}\n' \
               f'UUID: {self.uuid}\n' \
               f'Time: {self.time}\n' \
               f'IP: {self.ip}\n' \
               f'Screen: {self.screen_width} X {self.screen_height}\n' \
               f'TZ: {self.time_zone_hours}:{self.time_zone_mins}\n' \
               f'Datetime: {self.datetime}\n' \
               f'Browser: {self.browser} {self.browser_ver}\n' \
               f'OS: {self.os} {self.os_ver}\n' \
               f'Device: {self.device} {self.device_brand} {self.device_model}\n' \
               f'Mobile: {self.is_mobile}\n' \
               f'Tablet: {self.is_tablet}\n' \
               f'Touch: {self.is_touch_capable}\n' \
               f'PC: {self.is_pc}\n' \
               f'Bot: {self.is_bot}\n' \
               f'Behavior: {self.behaviour}\n'

    def start_event(self, time, body):
        self.time = time
        self.ip = body['ip']
        screen = body['screen_size'].split('x')
        self.screen_width = screen[0]
        self.screen_height = screen[1]
        time_zone = body['time_zone'].split(':')
        self.time_zone_hours = int(time_zone[0])
        self.time_zone_mins = int(time_zone[1])

        now = datetime.now(timezone.utc)
        delta = timedelta(hours=self.time_zone_hours, minutes=self.time_zone_mins)
        self.datetime = now + delta

        # handle agent data
        ua_string = body['agent']
        user_agent = parse(ua_string)

        self.browser = user_agent.browser.family  # returns 'Mobile Safari'
        self.browser_ver = user_agent.browser.version_string  # returns '5.1'

        # Accessing user agent's operating system properties
        self.os = user_agent.os.family  # returns 'iOS'
        self.os_ver = user_agent.os.version_string  # returns '5.1'

        # Accessing user agent's device properties
        self.device = user_agent.device.family  # returns 'iPhone'
        self.device_brand = user_agent.device.brand  # returns 'Apple'
        self.device_model = user_agent.device.model  # returns 'iPhone'

        self.is_mobile = user_agent.is_mobile
        self.is_tablet = user_agent.is_tablet
        self.is_touch_capable = user_agent.is_touch_capable
        self.is_pc = user_agent.is_pc
        self.is_bot = user_agent.is_bot

    def save_user(self):
        """save user to mongo"""

        user_obj = {
            'client': self.client,
            'uuid': self.uuid,
        }
        # TODO handle update of user
        mongo_client.uxpera.users.insert_one(user_obj)


if __name__ == '__main__':
    # execute only if run as a script
    client = 'demosite_001'
    uuid = 'ef222f6a-4967-4ef8-a74b-481db67e35ad'
    body_str = '{ "ip" : "5.29.40.204", "agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36", "screen_size" : "2560x1440", "time_zone" : "+3:30" }'
    body = json.loads(body_str)
    u = User(client, uuid)
    u.start_event(0, body)
    print(u)
