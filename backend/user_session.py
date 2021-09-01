import pandas as pd
import math
import random
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

        # load the behavior mapping, copy & cta tables
        self.behavior_mapping_df = None
        self.copy_df = None
        self.cta_df = None
        self._load_data_tables()

        # load the livia banners
        self.desktop_promotional_banner = ''
        self.desktop_review_banner = ''
        self.mobile_promotional_banner = ''
        self.mobile_review_banner = ''
        self._load_banners()

    def _load_data_tables(self):
        self.behavior_mapping_df = pd.read_excel('../data/behavior_mapping.xlsx')
        self.behavior_mapping_df['copy'] = self.behavior_mapping_df['copy'].apply(lambda x: x.split(','))
        self.behavior_mapping_df['cta'] = self.behavior_mapping_df['cta'].apply(lambda x: x.split(','))
        self.behavior_mapping_df.set_index('behavior', inplace=True)

        self.copy_df = pd.read_csv('../data/copy-general-livia.csv')
        self.cta_df = pd.read_csv('../data/cta-general.csv')

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

    def _calc_banner(self):
        copy = random.choice(self.behavior_mapping_df.loc[self.assumed_behaviour]['copy'])
        copy = int(copy)
        cta = random.choice(self.behavior_mapping_df.loc[self.assumed_behaviour]['cta'])
        cta = int(cta)
        print(f'behaviour={self.assumed_behaviour} copy={copy} cta={cta}')

        # check if to use promotional or review banner
        if copy % 100 == 6 or copy % 100 == 7:
            promotional = True
            html = self.desktop_promotional_banner
        else:
            promotional = False
            html = self.desktop_review_banner

        copy_text1 = self.copy_df[self.copy_df.id == copy].iloc[0]['copy1']
        copy_text2 = self.copy_df[self.copy_df.id == copy].iloc[0]['copy2']
        if type(copy_text2) == float and math.isnan(copy_text2):
            copy_text2 = ''
        cta_text = self.cta_df[self.cta_df.id == cta].iloc[0]['cta']
        if promotional:
            print('Promotional banner')
            print(f'copy_text="{copy_text1} {copy_text2}" cta_text="{cta_text}"')

            # replace text1
            html_id = html.find(id='ID33_OFF_ON_SUMMER_SALE_br')
            new = f'<div id="ID33_OFF_ON_SUMMER_SALE_br"><span>{copy_text1}</span></div>'
            new_soup = BeautifulSoup(new)
            html_id.replace_with(new_soup)

            # replace text2
            html_id = html.find(id='AND_EXTRA_REPLACEBLE_LIVIA_SKI_bq')
            new = f'<div id="AND_EXTRA_REPLACEBLE_LIVIA_SKI_bq"><span>{copy_text2}</span></div>'
            new_soup = BeautifulSoup(new)
            html_id.replace_with(new_soup)

            # replace cta
            html_id = html.find(id='SEE_PLANS_AND_PRICING')
            new = f'<div id="SEE_PLANS_AND_PRICING"><span>{cta_text}</span></div>'
            new_soup = BeautifulSoup(new)
            html_id.replace_with(new_soup)

        else:
            ref_text = self.copy_df[self.copy_df.id == copy].iloc[0]['ref']
            if type(ref_text) == float and math.isnan(ref_text):
                ref_text = ''
            print('Review banner')
            print(f'copy_text="{copy_text1} {copy_text2}" ref_text="{ref_text}" cta_text="{cta_text}"')

            # replace text1 & ref
            html_id = html.find(id='Livia_has_been_incredible_for_')
            new = f'<div id="Livia_has_been_incredible_for_"><span style="text-transform:uppercase;">{copy_text1} {copy_text2}</span>' \
                  f'<br><span style="font-family:Source Sans Pro;font-style:normal;font-weight:bold;font-size:20px;color:rgba(246,105,135,1);text-transform:uppercase;">{ref_text}</span></div>'
            new_soup = BeautifulSoup(new)
            html_id.replace_with(new_soup)

            # replace cta
            html_id = html.find(id='SEE_PLANS__PRICING')
            new = f'<div id="SEE_PLANS__PRICING"><span>{cta_text}</span></div>'
            new_soup = BeautifulSoup(new)
            html_id.replace_with(new_soup)

        return html

    def replace_generic_banner(self):
        # html = f'{self.assumed_behaviour} BANNER'
        html = self._calc_banner()
        command_sender.push_banner_to_user(self.client, self.uuid, str(html))
        self.replaced_generic_banner = True

