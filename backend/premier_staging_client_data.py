import pandas as pd
import math
import random
from bs4 import BeautifulSoup

from client_data import ClientData


class PremierStagingClientData(ClientData):
    def __init__(self):
        super().__init__('premier_staging')

        # TODO this should probably also be in a csv file

        self.dp_events = ['went_to_featured_products', 'went_to_category', 'search']
        self.bh_events = ['went_to_product_weekly_specials']
        self.nb_events = ['went_to_premier_world', 'went_to_free_samples']
        self.sl_events = ['went_to_gifts', 'went_to_best_sellers', 'went_to_blog', 'went_to_product_top_picks']
        self.sb_events = ['went_to_shipping_and_returns']

        # self.dp_events = ['search', 'search_bar', 'Product_Viewed']
        # self.bh_events = ['Clicked_Banner', 'promotions']
        # self.nb_events = ['hp_banner_custom']
        # self.sl_events = ['new_arrivals', 'best_sellers']
        # self.sb_events = ['reviews', 'timeout', 'terms_and_cond', 'security_and_priv', 'about_us', 'browsing_no_click',
        #                   'Scrolling_To_Second_Part', 'scrolling_to_third']

        self.long_time_events = ['went_to_terms_and_conditions', 'went_to_security_and_privacy', 'went_to_about_us',
                                 'Scrolling_To_Second_Part']
        self.medium_time_events = ['timeout']
        self.no_time_limit_events = ['went_to_affiliates', 'went_to_distributors', 'went_to_awards', 'went_to_contact',
                                     'went_to_media', 'went_to_account']

    def _load_data_tables(self):
        self.behavior_mapping_df = pd.read_excel(f'../clients/{self.client}/data/behavior_mapping.xlsx')
        self.behavior_mapping_df['copy'] = self.behavior_mapping_df['copy'].apply(lambda x: x.split(','))
        self.behavior_mapping_df['cta'] = self.behavior_mapping_df['cta'].apply(lambda x: x.split(','))
        self.behavior_mapping_df.set_index('behavior', inplace=True)

        self.copy_desktop_df = pd.read_excel(f'../clients/{self.client}/data/Premier Copy  2 Rows Desktop -Live.xlsx')
        self.copy_mobile_df = pd.read_excel(f'../clients/{self.client}/data/Premier Copy 4 Rows Mobile -Live.xlsx')
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

    @staticmethod
    def _match_link(link):
        return {
            'gifts': 'went_to_gifts',
            'gifts-under-50': 'went_to_gifts',
            'gifts-under-100': 'went_to_gifts',
            'gifts-under-200': 'went_to_gifts',
            'gifts-under-300': 'went_to_gifts',
            'more-gifts': 'went_to_gifts',
            'about-us': 'went_to_about_us',
            'contact': 'went_to_contact',
            '25th-anniversary': 'went_to_premier_world',
            'elements': 'went_to_premier_world',
            'premier-dead-sea-stores': 'went_to_premier_world',
            'in-the-media': 'went_to_premier_world',
            'celebs-love-premier': 'went_to_premier_world',
            'videos': 'went_to_premier_world',
            'reviews': 'went_to_premier_world',
            'elite-customer-care': 'went_to_premier_world',
            'international': 'went_to_distributors',
            'distributor-program': 'went_to_distributors',
            'become-a-retailer': 'went_to_affiliates',
            'awards': 'went_to_awards',
            'blog': 'went_to_blog',
            'best-sellers': 'went_to_best_sellers',
            'our-best-sellets': 'went_to_best_sellers',
            'award-winners': 'went_to_best_sellers',
            'gifts-for-her': 'went_to_best_sellers',
            'gifts-for-him': 'went_to_best_sellers',
            'terms-condition': 'went_to_terms_and_conditions',
            'privacy_policy': 'went_to_security_and_privacy',
            'the-dead-sea': 'went_to_category',
            'salt-therapy': 'went_to_category',
            'dead-sea-watch': 'went_to_category',
            'guide-dead-sea-mud-mask': 'went_to_category',
            'dead-sea-minerals-premier': 'went_to_category',
            'dead-sea-salt': 'went_to_category',
            'free-face-mask': 'went_to_free_samples',
            'shipping-returns': 'went_to_shipping_and_returns',
        }.get(link, None)  # None is default if title is not found

    @staticmethod
    def _match_link_category(link_parts):
        if ' classic-skincare' in link_parts:
            return 'went_to_category'
        elif 'prestige-skincare' in link_parts:
            return 'went_to_category'
        elif 'supreme-skincare' in link_parts:
            return 'went_to_category'
        elif 'makeup' in link_parts:
            return 'went_to_category'
        elif 'account' in link_parts:
            return 'went_to_account'

    @staticmethod
    def _match_data(data_str):
        return {
            'Featured': 'went_to_featured_products',
            'Weekly Specials': 'went_to_product_weekly_specials',
            'Top Picks': 'went_to_product_top_picks',
        }.get(data_str, None)  # None is default if title is not found

    @staticmethod
    def _match_title(title):
        return {
            'Social media': 'went_to_media',
        }.get(title, None)  # None is default if title is not found

    def _get_canonical_event_type(self, event):
        result = event.event_type

        # print(result == 'link')
        # print(event.body is not None)
        # print('link' in event.body)
        # print(event.body)
        if result == 'link' and event.body is not None and 'link' in event.body:
            print(f'^^^ Testing link event link')
            link = event.body['link']
            link = link.split('/')[-1]
            match = self._match_link(link)
            if match is not None:
                print(f'^^^ Mapped link event to {match}')
                return match
        if result == 'link' and event.body is not None and 'link' in event.body:
            print(f'^^^ Testing link event link category')
            link = event.body['link']
            link_parts = link.split('/')
            match = self._match_link_category(link_parts)
            if match is not None:
                print(f'^^^ Mapped link event to {match}')
                return match
        elif result == 'button' and event.body is not None and 'data' in event.body:
            print(f'^^^ Testing button event data')
            data_str = event.body['data']
            match = self._match_data(data_str)
            if match is not None:
                print(f'^^^ Mapped button event to {match}')
                return match
        elif result == 'button' and event.body is not None and 'title' in event.body:
            print(f'^^^ Testing button event title')
            title = event.body['title']
            match = self._match_title(title)
            if match is not None:
                print(f'^^^ Mapped button event to {match}')
                return match

        return result

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
