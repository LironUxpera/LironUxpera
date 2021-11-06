# event class

import math
import json
from datetime import datetime, timedelta, timezone
from user_agents import parse
from pymongo import MongoClient
from pymongo.errors import InvalidOperation

from event import Event
from send_command import SendCommand

mongo_client = MongoClient()
command_sender = SendCommand()


class User:
    def __init__(self, client, uuid):
        self.new_session_hours_delta = 24  # num of hours between last session to declare a new session started
        self.client = client
        self.uuid = uuid

        # global info
        self.last_time = '0'  # last recorded time of event
        self.first_visit_dt = None  # first visit date
        self.last_visit_dt = None  # last visit date
        self.sessions = 0  # num of sessions
        self.assumed_behaviour = ''  # DP,SL, NBS, BH, SB
        self.behaviour_changed = False
        self.behaviour_escalated = False
        self.bought_anything = False
        self.bought_last_session = False

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
        self.events = []

        # check if user exists in mongo and if so read in data
        self.new_user = True
        record = self._find_user()
        if record:
            self.new_user = False
            self.last_time = record['last_time']
            self.first_visit_dt = record['first_visit_dt']
            # self.first_visit_dt.replace(tzinfo=timezone.utc)
            self.last_visit_dt = record['last_visit_dt']
            # self.first_visit_dt.replace(tzinfo=timezone.utc)
            self.sessions = record['sessions']
            self.assumed_behaviour = record['assumed_behaviour']
            self.behaviour_changed = record['behaviour_changed']
            self.behaviour_escalated = record['behaviour_escalated']
            self.bought_anything = record['bought_anything']
            self.bought_last_session = record['bought_last_session']

            # get latest session
            session = self._find_latest_session()
            self.time = session['time']
            self.ip = session['ip']
            self.screen_width = session['screen_width']
            self.screen_height = session['screen_height']
            self.time_zone_hours = session['time_zone_hours']
            self.time_zone_mins = session['time_zone_mins']
            self.datetime = session['datetime']
            self.browser = session['browser']
            self.browser_ver = session['browser_ver']
            self.os = session['os']
            self.os_ver = session['os_ver']
            self.device = session['device']
            self.device_brand = session['device_brand']
            self.device_model = session['device_model']
            self.is_mobile = session['is_mobile']
            self.is_tablet = session['is_tablet']
            self.is_touch_capable = session['is_touch_capable']
            self.is_pc = session['is_pc']
            self.is_bot = session['is_bot']
            self.behaviour = session['behaviour']

            # gets events turning them into Event objects
            event_objs = session['events']
            events = []
            for e in event_objs:
                event = Event()
                event.from_dict(self.client, self.uuid, e)
            self.events = events

        print('New User')
        print('========')
        print(self)

    def __str__(self):
        user_str = f'Client: {self.client}\n' \
                   f'UUID: {self.uuid}\n' \
                   f'New User: {self.new_user}\n' \
                   f'First: {self.first_visit_dt}\n' \
                   f'Last: {self.last_visit_dt}\n' \
                   f'Sessions: {self.sessions}\n' \
                   f'Assumed behaviour: {self.assumed_behaviour}\n' \
                   f'Behaviour changed: {self.behaviour_changed}\n' \
                   f'Behaviour escalated: {self.behaviour_escalated}\n' \
                   f'Bought anything: {self.bought_anything}\n' \
                   f'Bought last session: {self.bought_last_session}\n'

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
        record = mongo_client.uxpera.users.find_one({'client': self.client, 'uuid': self.uuid})
        return record

    def save_user(self):
        # TODO add support for dirty flag / user_object with changes so we save only what is needed and when needed

        user_obj = {
            'client': self.client,
            'uuid': self.uuid,
            'last_time' : self.last_time,
            'first_visit_dt': self.first_visit_dt,
            'last_visit_dt': self.last_visit_dt,
            'sessions': self.sessions,
            'assumed_behaviour': self.assumed_behaviour,
            'behaviour_changed': self.behaviour_changed,
            'behaviour_escalated': self.behaviour_escalated,
            'bought_anything': self.bought_anything,
            'bought_last_session': self.bought_last_session,

            # 'events': [e.to_dict(full=False) for e in self.events]
        }
        if self.new_user:
            result = mongo_client.uxpera.users.insert_one(user_obj)
            if result:
                self.new_user = False
            return result
        else:
            result = mongo_client.uxpera.users.update_one({'client': self.client, 'uuid': self.uuid}, {'$set': user_obj})
            try:
                return result.acknowledged and result.matched_count == 1
            except InvalidOperation:
                return False

    def _find_latest_session(self):
        result = None
        cursor = mongo_client.uxpera.userSessions.find({'client': self.client, 'uuid': self.uuid})
        for session in cursor:
            if result is None:
                result = session
            else:
                # take session with largest time) i.e. latest)
                if session['time'] > result['time']:
                    result = session
        return result

    def _save_user_session(self):
        session_obj = {
            'client': self.client,
            'uuid': self.uuid,
            'time': self.time,
            'ip': self.ip,
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
            'time_zone_hours': self.time_zone_hours,
            'time_zone_mins': self.time_zone_mins,
            'datetime': self.datetime,
            'browser': self.browser,
            'browser_ver': self.browser_ver,
            'os': self.os,
            'os_ver': self.os_ver,
            'device': self.device,
            'device_brand': self.device_brand,
            'device_model': self.device_model,
            'is_mobile': self.is_mobile,
            'is_tablet': self.is_tablet,
            'is_touch_capable': self.is_touch_capable,
            'is_pc': self.is_pc,
            'is_bot': self.is_bot,
            'behaviour': self.behaviour,
        }
        result = mongo_client.uxpera.userSessions.insert_one(session_obj)
        return result

    def _update_session_events(self):
        session_obj = {
            'events': [e.to_dict(full=False) for e in self.events]
        }
        result = mongo_client.uxpera.userSessions.update_one({'client': self.client, 'uuid': self.uuid}, {'$set': session_obj})
        try:
            return result.acknowledged and result.matched_count == 1
        except InvalidOperation:
            return False

    def _get_local_datetime(self):
        now = datetime.now()
        delta = timedelta(hours=self.time_zone_hours, minutes=self.time_zone_mins)
        return now + delta

    def get_events(self):
        return self.events

    def get_behaviour(self):
        return self.assumed_behaviour

    def set_behaviour(self, behaviour):
        self.assumed_behaviour = behaviour

    def add_event(self, event):
        # save event
        self.events.append(event)

        # TODO confirm session event with Amir
        if event.event_type == 'start' or event.event_type == 'session':
            self.start_event(event.time, event.body)
            self.sessions += 1
            self._save_user_session()
        else:
            # other types of events - do nothing for now
            pass

        # save the changed session events - here so we are sure we have session data
        self._update_session_events()

        self.last_time = event.time

        # if this event is longer than new_session_hours_delta, then we need to request to get new session data
        now = self._get_local_datetime()
        if self.last_visit_dt is not None:
            print(now.tzinfo, self.last_visit_dt.tzinfo)
            
            duration = now - self.last_visit_dt
            duration_in_s = duration.total_seconds()
            hours = divmod(duration_in_s, 3600)[0]
            if hours >= self.new_session_hours_delta:
                command_sender.request_user_session_info()

        # update timers
        if len(self.events) == 1:
            self.first_visit_dt = self._get_local_datetime()
        self.last_visit_dt = self._get_local_datetime()

        print('Add event to User')
        print('========')
        print(self)

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

        self.datetime = self._get_local_datetime()

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

    def user_not_accessed_for_x_hours_ago(self, hours):
        if self.last_visit_dt is None:
            return False

        now = self._get_local_datetime()
        duration = now - self.last_visit_dt
        duration_in_s = duration.total_seconds()
        hours_diff = divmod(duration_in_s, 3600)[0]
        return hours_diff >= hours


if __name__ == '__main__':
    # execute only if run as a script
    client = 'demosite_001'
    uuid = 'ef222f6a-4967-4ef8-a74b-481db67e35ad'
    body_str = '{ "ip" : "5.29.40.204", "agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36", "screen_size" : "2560x1440", "time_zone" : "+3.5" }'
    body = json.loads(body_str)
    u = User(client, uuid)
    u.start_event(0, body)
    print(u)
