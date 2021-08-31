import pandas as pd
from bs4 import BeautifulSoup
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
        self.dp_events = ['search', 'search_bar', 'Product_Viewed']
        self.bh_events = ['Clicked_Banner', 'promotions']
        self.nb_events = ['hp_banner_custom']
        self.sl_events = ['new_arrivals', 'best_sellers']
        self.sb_events = ['reviews']
        self.sb_10_sec_events = ['terms_and_cond', 'security_and_priv', 'about_us', 'browsing_no_click',
                          'Scrolling_To_Second_Part', 'scrolling_to_third']

        # load the livia banners
        self.desktop_promotional_banner = ''
        self.desktop_review_banner = ''
        self.mobile_promotional_banner = ''
        self.mobile_review_banner = ''
        self._load_banners()

    def _load_banners(self):
        with open('../banners/desktop_1000x100_promotional.html', 'rt') as file:
            self.desktop_promotional_banner = BeautifulSoup(file.read(), features="html.parser")
        with open('../banners/desktop_1000x100_review.html', 'rt') as file:
            self.desktop_review_banner = BeautifulSoup(file.read(), features="html.parser")
        with open('../banners/android_720_X150_promotional.html', 'rt') as file:
            self.mobile_promotional_banner = BeautifulSoup(file.read(), features="html.parser")
        with open('../banners/android_720_review.html', 'rt') as file:
            self.mobile_review_banner = BeautifulSoup(file.read(), features="html.parser")

    def add_event(self, event):
        print('User Add event')
        self.events.append(event)
        if not self.replaced_generic_banner:
            behavior = self.check_behaviour()
            if behavior:
                print(f'== Behaviour={behavior}')
                self.assumed_behaviour = behavior
                self.replace_generic_banner()

    def check_behaviour(self):
        behaviour = ''
        if not self.events:
            return behaviour

        last_event = self.events[-1]
        last_time = last_event.time
        last_type = last_event.event_type
        print(f'== Checking time={last_time} event={last_type}')

        # for now check only for events in first 5 seconds
        if last_time > 10000 and last_type in self.sb_10_sec_events:
            behaviour = 'SB'
            return behaviour

        # left only to check for events in first 5 seconds
        if last_time > 5000:
            return behaviour

        if last_type in self.dp_events:
            behaviour = 'DP'
        elif last_type in self.bh_events:
            behaviour = 'BH'
        elif last_type in self.nb_events:
            behaviour = 'NBS'
        elif last_type in self.sl_events:
            behaviour = 'SL'
        elif last_type in self.sb_events:
            behaviour = 'SB'

        return behaviour

    def replace_generic_banner(self):
        html = self.desktop_promotional_banner.find(id='SEE_PLANS_AND_PRICING')
        new = f'<div id="SEE_PLANS_AND_PRICING"><span>{self.assumed_behaviour} BANNER</span></div>'
        new_soup = BeautifulSoup(new)
        html.replace_with(new_soup)
        # html = f'{self.assumed_behaviour} BANNER'

        command_sender.push_banner_to_user(self.client, self.uuid, str(html))
        self.replaced_generic_banner = True

