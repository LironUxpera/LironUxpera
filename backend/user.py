# event class

import math
import json
from datetime import datetime, timedelta, timezone
from user_agents import parse
from pymongo import MongoClient
from pymongo.errors import InvalidOperation


mongo_client = MongoClient()
db = mongo_client.uxpera
# users = db.user
# user_sessions = db.userSession


class User:
    def __init__(self, client, uuid):
        self.client = client
        self.uuid = uuid

        # global info
        self.assumed_behaviour = ''  # DP,SL, NBS, BH, SB
        self.last_time = '0'  # last recorded time of event
        self.first_visit_dt = None  # first visit date
        self.last_visit_dt = None  # last visit date
        self.sessions = 0  # num of sessions
        self.events = []

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

        # check if user exists in mongo and if so read in data
        self.new_user = True
        record = self._find_user()
        if record:
            self.new_user = False
            self.assumed_behaviour = record['assumed_behaviour']
            self.last_time = record['last_time']
            self.first_visit_dt = record['first_visit_dt']
            self.last_visit_dt = record['last_visit_dt']
            self.sessions = record['sessions']
            self.events = record['events']

        print('New User')
        print('========')
        print(self)

    def __str__(self):
        user_str = f'Client: {self.client}\n' \
                   f'UUID: {self.uuid}\n' \
                   f'New User: {self.new_user}\n' \
                   f'Assumed behaviour: {self.assumed_behaviour}\n' \
                   f'First: {self.first_visit_dt}\n' \
                   f'Last: {self.last_visit_dt}\n' \
                   f'Sessions: {self.sessions}\n'

        session_str = f'Time: {self.time}\n' \
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

        return user_str + '\nSession:\n' + session_str

    def _find_user(self):
        record = db.user.find_one({'client': self.client, 'uuid': self.uuid})
        return record

    def _save_user(self):
        user_obj = {
            'client': self.client,
            'uuid': self.uuid,
            'assumed_behaviour': self.assumed_behaviour,
            'first_visit_dt': self.first_visit_dt,
            'last_visit_dt': self.last_visit_dt,
            'sessions': self.sessions,
        }
        if self.new_user:
            result = mongo_client.uxpera.users.insert_one(user_obj)
            return result
        else:
            result = mongo_client.uxpera.users.update_one({'client': self.client, 'uuid': self.uuid}, {'$set': user_obj})
            try:
                return result.acknowledged and result.matched_count == 1
            except InvalidOperation:
                return False

    def events(self):
        return self.events

    def get_behaviour(self):
        return self.assumed_behaviour

    def set_behaviour(self, behaviour):
        self.assumed_behaviour = behaviour

    def add_event(self, event):
        # save event
        self.events.append(event)

        # TODO confirm session event with Amir
        if event.event_type == 'start' or 'session':
            self.start_event(event.time, event.body)
            # TODO save session
        else:
            # other types of events
            # TODO handle sessions
            pass

        # TODO handle changes based on event

        print('Add event to User')
        print('========')
        print(self)

        # save user
        self._save_user()

    def start_event(self, time, body):
        self.time = time
        self.ip = body['ip']
        screen = body['screen_size'].split('x')
        self.screen_width = screen[0]
        self.screen_height = screen[1]
        time_zone = body['time_zone']
        frac, whole = math.modf(float(time_zone))
        self.time_zone_hours = int(whole)
        self.time_zone_mins = int(frac * 60)

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


if __name__ == '__main__':
    # execute only if run as a script
    client = 'demosite_001'
    uuid = 'ef222f6a-4967-4ef8-a74b-481db67e35ad'
    body_str = '{ "ip" : "5.29.40.204", "agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36", "screen_size" : "2560x1440", "time_zone" : "+3.5" }'
    body = json.loads(body_str)
    u = User(client, uuid)
    u.start_event(0, body)
    print(u)
