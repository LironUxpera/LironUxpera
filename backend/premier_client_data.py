import pandas as pd
import math
import random
from bs4 import BeautifulSoup

from client_data import ClientData


class PremierClientData(ClientData):
    def __init__(self):
        super().__init__('permier')

        # TODO this should probably also be in a csv file
        # TODO update with premier events
        self.dp_events = ['search', 'search_bar', 'Product_Viewed']
        self.bh_events = ['Clicked_Banner', 'promotions']
        self.nb_events = ['hp_banner_custom']
        self.sl_events = ['new_arrivals', 'best_sellers']
        self.sb_events = ['reviews', 'timeout', 'terms_and_cond', 'security_and_priv', 'about_us', 'browsing_no_click',
                          'Scrolling_To_Second_Part', 'scrolling_to_third']

    def _load_data_tables(self):
        self.behavior_mapping_df = pd.read_excel(f'../clients/{self.client}/data/behavior_mapping.xlsx')
        self.behavior_mapping_df['copy'] = self.behavior_mapping_df['copy'].apply(lambda x: x.split(','))
        self.behavior_mapping_df['cta'] = self.behavior_mapping_df['cta'].apply(lambda x: x.split(','))
        self.behavior_mapping_df.set_index('behavior', inplace=True)

        self.copy_desktop_df = pd.read_excel(f'../clients/{self.client}/data/Premier Copy  2 Rows Desktop -Live.xlsx')
        self.copy_mobile_df = pd.read_excel(f'../clients/{self.client}/data/Premier Copy 4 Rows Mobile -Live.csv')
        self.cta_df = pd.read_csv(f'../clients/{self.client}/data/cta-general.csv')

    def _load_banners(self):
        return

        # with open(f'../clients/{self.client}/banners/desktop_1000x100_promotional.html', 'rt') as file:
        #     self.desktop_promotional_banner = BeautifulSoup(file.read(), features="html.parser")
        # with open(f'../clients/{self.client}/banners/desktop_1000x100_review.html', 'rt') as file:
        #     self.desktop_review_banner = BeautifulSoup(file.read(), features="html.parser")
        # with open(f'../clients/{self.client}/banners/android_720_X150_promotional.html', 'rt') as file:
        #     self.mobile_promotional_banner = BeautifulSoup(file.read(), features="html.parser")
        # with open(f'../clients/{self.client}/banners/android_720_review.html', 'rt') as file:
        #     self.mobile_review_banner = BeautifulSoup(file.read(), features="html.parser")

    def calc_banner(self, assumed_behaviour):
        return ''

        copy = random.choice(self.behavior_mapping_df.loc[assumed_behaviour]['copy'])
        copy = int(copy)
        cta = random.choice(self.behavior_mapping_df.loc[assumed_behaviour]['cta'])
        cta = int(cta)
        print(f'behaviour={assumed_behaviour} copy={copy} cta={cta}')

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
