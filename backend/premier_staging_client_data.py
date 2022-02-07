import pandas as pd
import math
import random
from bs4 import BeautifulSoup

from client_data import ClientData


class PremierStagingClientData(ClientData):
    def __init__(self):
        super().__init__('premier_staging')

        # TODO this should probably also be in a csv file

        self.dp_events = ['went_to_featured_products', 'went_to_category', 'search', 'went_to_searchbar']
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

        self.long_time_events = ['went_to_terms_and_conditions', 'went_to_security_and_privacy', 'went_to_about_us']
        self.timeout_events = ['timeout']
        self.scroll_events = ['Scrolling_To_Second_Part']
        self.no_time_limit_events = ['went_to_affiliates', 'went_to_distributors', 'went_to_awards', 'went_to_contact',
                                     'went_to_media', 'went_to_account']

    def _load_data_tables(self):
        self.behavior_mapping_df = pd.read_excel(f'../clients/{self.client}/data/behavior_mapping.xlsx')
        self.behavior_mapping_df['copy'] = self.behavior_mapping_df['copy'].apply(lambda x: x.split(','))
        self.behavior_mapping_df['cta'] = self.behavior_mapping_df['cta'].apply(lambda x: x.split(','))
        self.behavior_mapping_df.set_index('behavior', inplace=True)

        self.products_df = pd.read_csv(f'../clients/{self.client}/data/premier_products.csv')
        self.best_sellers_df = pd.read_excel(f'../clients/{self.client}/data/Best Sellers-LIVE.xlsx')
        self.copy4_df = pd.read_excel(f'../clients/{self.client}/data/Premier Copy  2 Rows Desktop -Live.xlsx')
        self.copy2_df = pd.read_excel(f'../clients/{self.client}/data/Premier Copy 4 Rows Mobile -Live.xlsx')
        self.cta_df = pd.read_csv(f'../clients/{self.client}/data/cta-general.csv')

    def _load_banners(self):
        # home page
        with open(f'../clients/{self.client}/banners/Behaviour-Desktop-1920x650-R.html', 'rt') as file:
            self.desktop_hp_testimonial_banner = BeautifulSoup(file.read(), features="html.parser")
        with open(f'../clients/{self.client}/banners/Behaviour-Desktop-1920x650.html', 'rt') as file:
            self.desktop_hp_promotional_banner = BeautifulSoup(file.read(), features="html.parser")
        with open(f'../clients/{self.client}/banners/Behaviour-Mobile-6600x770_R.html', 'rt') as file:
            self.mobile_hp_testimonial_banner = BeautifulSoup(file.read(), features="html.parser")
        with open(f'../clients/{self.client}/banners/Behaviour-Mobile-6600x770.html', 'rt') as file:
            self.mobile_hp_promotional_banner = BeautifulSoup(file.read(), features="html.parser")

        # product page
        with open(f'../clients/{self.client}/banners/Behaviour-Desktop-192x112-R.html', 'rt') as file:
            self.desktop_pp_testimonial_banner = BeautifulSoup(file.read(), features="html.parser")
        with open(f'../clients/{self.client}/banners/Behaviour-Desktop-192x112.html', 'rt') as file:
            self.desktop_pp_promotional_banner = BeautifulSoup(file.read(), features="html.parser")
        with open(f'../clients/{self.client}/banners/Behaviour-Mobile-400x62.html', 'rt') as file:
            self.mobile_pp_promotional_banner = BeautifulSoup(file.read(), features="html.parser")

        # checkout page
        self.desktop_cp_testimonial_banner = self.desktop_pp_testimonial_banner
        self.desktop_cp_promotional_banner = self.desktop_pp_promotional_banner
        self.mobile_cp_promotional_banner = self.mobile_pp_promotional_banner

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
        if 'classic-skincare' in link_parts:
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
            'search-button': 'went_to_searchbar',
            'Social media': 'went_to_media',
        }.get(title, None)  # None is default if title is not found

    def _get_canonical_event_type(self, event):
        result = event.event_type
        # print('Event TYPE == ', result)
        # print(result == 'link')
        # print(event.body is not None)
        # print('link' in event.body)
        # print(event.body)

        if result == 'link' and event.body is not None and 'link' in event.body and not event.body['link'] is None:
            link = event.body['link']
            print(f'^^^ Testing link event link', link)
            link = link.split('/')[-1]
            match = self._match_link(link)
            if match is not None:
                print(f'^^^ Mapped link event to {match}')
                return match
        if result == 'link' and event.body is not None and 'link' in event.body and not event.body['link'] is None:
            link = event.body['link']
            print(f'^^^ Testing link event link category', link)
            link_parts = link.split('/')
            match = self._match_link_category(link_parts)
            if match is not None:
                print(f'^^^ Mapped link event to {match}')
                return match
        elif result == 'button' and event.body is not None and 'data' in event.body and not event.body['data'] is None:
            data_str = event.body['data']
            print(f'^^^ Testing button event data', data_str)
            match = self._match_data(data_str)
            if match is not None:
                print(f'^^^ Mapped button event to {match}')
                return match
        elif result == 'button' and event.body is not None and 'title' in event.body and not event.body['title'] is None:
            title = event.body['title']
            print(f'^^^ Testing button event title', title)
            match = self._match_title(title)
            if match is not None:
                print(f'^^^ Mapped button event to {match}')
                return match

        return result

    def _get_random_best_seller(self):
        return self.best_sellers_df.sample(1)['id'].values[0]

    def _get_product_info(self, prod_id):
        prod = self.products_df[self.products_df.id == prod_id]
        if len(prod) == 0:
            return '', '', ''

        title = prod['title'].values[0]
        link = prod['title'].values[0]
        image_link = prod['image_link'].values[0]
        return title, link, image_link

    def _get_cta_id_for_behaviour(self, behaviour):
        table = {
            'BH': [911, 912],
            'DP': [1011, 1012],
            'SL': [1111, 1112],
            'SB': [1211, 1212],
            'NBS': [1311, 1312],
        }

        # BH:  # 900-#910
        # DP:  # 909,#1000-#1012
        # SL:  # 1100,#1004,#1101, #1002,#910,#1102,#1103,#903,#904,#905,#1008,#1009,#1104,#909
        # SB:  # 1100,#1200-#1205
        # NBS:  # 1004,#1101,#1203,#1300,#1202,#1301,#1302,#1200,#1201,#1204.

        # get random from behaviour list
        cta_list = table[behaviour]
        return random.choice(cta_list)

    def _get_cta_for_cta_id(self, cta_id):
        cta = self.cta_df[self.cta_df.id == cta_id]
        if len(cta) == 0:
            return ''

        return cta['cta'].values[0]

    def _get_copy4_for_prod_id(self, prod_id):
        copy = self.copy4_df[self.copy4_df.prod_id == prod_id]
        if len(copy) == 0:
            return ''

        copy = copy.sample(1)

        if 'row1' in copy:
            row1 = copy['row1'].values[0]
        else:
            row1 = ''
        if 'row2' in copy:
            row2 = copy['row2'].values[0]
        else:
            row2 = ''
        if 'row3' in copy:
            row3 = copy['row3'].values[0]
        else:
            row3 = ''
        if 'row4' in copy:
            row4 = copy['row4'].values[0]
        else:
            row4 = ''
        if 'name' in copy:
            name = copy['name'].values[0]
        else:
            name = ''
        return row1, row2, row3, row4, name

    def _get_copy2_for_prod_id(self, prod_id):
        copy = self.copy4_df[self.copy4_df.prod_id == prod_id]
        if len(copy) == 0:
            return ''

        copy = copy.sample(1)

        if 'row1' in copy:
            row1 = copy['row1'].values[0]
        else:
            row1 = ''
        if 'row2' in copy:
            row2 = copy['row2'].values[0]
        else:
            row2 = ''
        if 'name' in copy:
            name = copy['name'].values[0]
        else:
            name = ''
        return row1, row2, name

    # home page

    def calc_desktop_hp_testimonial_banner(self, copy_text1, copy_text2, cta_text, user_name, product_name):
        html = self.desktop_hp_testimonial_banner

        # replace text
        html_id = html.find(id='My_bath_time_is_never_complete')
        new = f'<div id="My_bath_time_is_never_complete">' \
              f'<span>"{copy_text1}</span><br/><span>{copy_text2}”</span><br/>' \
              f'</div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        # replace user name
        html_id = html.find(id='n____John_B')
        new = f'<div id="n____John_B">' \
              f'<span></span><br/><span></span><br/><span></span><br/><span></span><br/>' \
              f'<span">{user_name}.</span>' \
              f'</div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        # replace cta
        html_id = html.find(id='TAKE_THE_NEXT_SETP')
        new = f'<div id="TAKE_THE_NEXT_SETP"><span>{cta_text}</span></div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        # replace product name
        html_id = html.find(id='PERFECTION_REFINING_FACIAL_PEE')
        new = f'<div id="PERFECTION_REFINING_FACIAL_PEE"><span>{product_name}</span><br/>/div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        return html

    def calc_desktop_hp_promotional_banner(self, copy_text1, copy_text2, cta_text, product_name):
        html = self.desktop_hp_promotional_banner

        # replace text
        html_id = html.find(id='n_3_OFF_ON_SUMMER_SALEXXX_BUY_')
        new = f'<div id="n_3_OFF_ON_SUMMER_SALEXXX_BUY_">' \
              f'<span">{copy_text1}</span><br/>' \
              f'<span">{copy_text2}</span><br/>' \
              f'</div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        # replace cta
        html_id = html.find(id='TAKE_THE_NEXT_SETP')
        new = f'<div id="TAKE_THE_NEXT_SETP"><span>{cta_text}</span></div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        # replace product name
        html_id = html.find(id='PERFECTION_REFINING_FACIAL_PEE')
        new = f'<div id="PERFECTION_REFINING_FACIAL_PEE"><span>{product_name}</span><br/>/div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        return html

    def calc_mobile_hp_testimonial_banner(self, copy_text1, copy_text2, copy_text3, copy_text4, cta_text,
                                          user_name, product_name):
        html = self.mobile_hp_testimonial_banner

        # replace text
        html_id = html.find(id='MY_BATH_TIME_IS_NEVER_COMPLETE')
        new = f'<div id="MY_BATH_TIME_IS_NEVER_COMPLETE">' \
              f'<span>"{copy_text1}</span><br/><span>{copy_text2}”</span><br/>' \
              f'<span>"{copy_text3}</span><br/><span>{copy_text4}”</span><br/>' \
              f'</div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        # replace user name
        # TODO Liron - missing!
        # html_id = html.find(id='n____John_B')
        # new = f'<div id="n____John_B">' \
        #       f'<span></span><br/><span></span><br/><span></span><br/><span></span><br/>' \
        #       f'<span style="font-size:39.0897102355957px;">{user_name}.</span>' \
        #       f'</div>'
        # new_soup = BeautifulSoup(new, features='html.parser')
        # html_id.replace_with(new_soup)

        # replace cta
        html_id = html.find(id='TAKE_THE_NEXT_SETP')
        new = f'<div id="TAKE_THE_NEXT_SETP"><span>{cta_text}</span></div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        # replace product name
        html_id = html.find(id='PERFECTION_REFINING_FACIAL_PEE')
        new = f'<div id="PERFECTION_REFINING_FACIAL_PEE"><span>{product_name}</span><br/>/div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        return html

    def calc_mobile_hp_promotional_banner(self, copy_text1, copy_text2, cta_text, product_name):
        html = self.mobile_hp_promotional_banner

        # replace text
        html_id = html.find(id='n_3_OFF_ON_SUMMER_SALE_XXX_BUY')
        new = f'<div id="n_3_OFF_ON_SUMMER_SALE_XXX_BUY">' \
              f'<span">{copy_text1}</span><br/>' \
              f'<span">{copy_text2}</span><br/>' \
              f'</div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        # replace cta
        html_id = html.find(id='TAKE_THE_NEXT_SETP')
        new = f'<div id="TAKE_THE_NEXT_SETP"><span>{cta_text}</span></div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        # replace product name
        html_id = html.find(id='PERFECTION_REFINING_FACIAL_PEE')
        new = f'<div id="PERFECTION_REFINING_FACIAL_PEE"><span>{product_name}</span><br/>/div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        return html

    # product page

    def calc_desktop_pp_testimonial_banner(self, copy_text1, copy_text2, user_name):
        html = self.desktop_pp_testimonial_banner

        # replace text
        html_id = html.find(id='My_bath_time_is_never_complete')
        new = f'<div id="My_bath_time_is_never_complete">' \
              f'<span>"{copy_text1}</span><br/><span>{copy_text2}”</span><br/>' \
              f'<span>"{user_name}</span>' \
              f'</div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        return html

    def calc_desktop_pp_promotional_banner(self, copy_text1, copy_text2):
        html = self.desktop_pp_promotional_banner

        # replace text
        html_id = html.find(id='n_3_OFF_ON_SUMMER_SALE_XXX_BUY')
        new = f'<div id="n_3_OFF_ON_SUMMER_SALE_XXX_BUY">' \
              f'<span">{copy_text1}</span><br/>' \
              f'<span">{copy_text2}</span>' \
              f'</div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        return html

    def calc_mobile_pp_promotional_banner(self, copy_text1, copy_text2):
        html = self.mobile_pp_promotional_banner

        # replace text
        html_id = html.find(id='n_5_OFF__2ND_ITEM__ORDERS_OVER')
        new = f'<div id="n_5_OFF__2ND_ITEM__ORDERS_OVER">' \
              f'<span style="font-size:9.801440238952637px;letter-spacing:-0.1px;">{copy_text1}</span><br/>' \
              f'<span style="font-size:9.801440238952637px;letter-spacing:-0.1px;">{copy_text2}</span><br/>' \
              f'</div>'
        new_soup = BeautifulSoup(new, features='html.parser')
        html_id.replace_with(new_soup)

        return html

    # cart page

    def calc_desktop_cp_testimonial_banner(self, copy_text1, copy_text2, user_name):
        return self.calc_desktop_pp_testimonial_banner(copy_text1, copy_text2, user_name)

    def calc_desktop_cp_promotional_banner(self, copy_text1, copy_text2):
        return self.calc_desktop_pp_promotional_banner(copy_text1, copy_text2)

    def calc_mobile_cp_promotional_banner(self,  copy_text1, copy_text2):
        return self.calc_mobile_pp_promotional_banner( copy_text1, copy_text2)

    def calc_banner(self, assumed_behaviour, page_type, is_mobile):
        # copy = random.choice(self.behavior_mapping_df.loc[assumed_behaviour]['copy'])
        # copy = int(copy)
        # cta = random.choice(self.behavior_mapping_df.loc[assumed_behaviour]['cta'])
        # cta = int(cta)
        # print(f'behaviour={assumed_behaviour} copy={copy} cta={cta}')
        #
        # # check if to use promotional or review banner
        # if copy % 100 == 6 or copy % 100 == 7:
        #     promotional = True
        #     html = self.desktop_promotional_banner
        # else:
        #     promotional = False
        #     html = self.desktop_review_banner
        #
        # copy_text1 = self.copy_df[self.copy_df.id == copy].iloc[0]['copy1']
        # copy_text2 = self.copy_df[self.copy_df.id == copy].iloc[0]['copy2']
        # if type(copy_text2) == float and math.isnan(copy_text2):
        #     copy_text2 = ''
        # cta_text = self.cta_df[self.cta_df.id == cta].iloc[0]['cta']

        # select a random product and get it's details
        prod_id = self._get_random_best_seller()
        title, link, image_link = self._get_product_info(prod_id)
        print('Selected best seller', prod_id, title)

        # copy 4
        row1, row2, row3, row4, name = self._get_copy4_for_prod_id(prod_id)
        copy_text1 = row1
        copy_text2 = row2
        copy_text3 = row3
        copy_text4 = row4
        user_name = name

        # copy_text1 = 'Copy text 1 ' + assumed_behaviour
        # copy_text2 = 'Copy text 2 ' + assumed_behaviour
        # copy_text3 = 'Copy text 3 ' + assumed_behaviour
        # copy_text4 = 'Copy text 4 ' + assumed_behaviour
        # user_name = 'Harry H'

        # copy 2
        row1, row2, name = self._get_copy2_for_prod_id(prod_id)
        copy2_text1 = row1
        copy2_text2 = row2
        user2_name = name

        # CTA
        cta_id = self._get_cta_id_for_behaviour(assumed_behaviour)
        cta_text = self._get_cta_for_cta_id(cta_id)
        # cta_text = 'Call to action ' + assumed_behaviour

        product_name = title

        print('@@@@ Banner: ', assumed_behaviour, page_type, is_mobile)
        print(f'copy_text="{copy_text1} {copy_text2} {copy_text3} {copy_text4}" cta_text="{cta_text}"')
        print(f'copy2_text="{copy2_text1} {copy2_text2}""')
        testimonial = random.choice([True, False])

        if page_type == 'hp':
            # home page
            if not is_mobile:
                if testimonial:
                    print('Testimonial banner')
                    return self.calc_desktop_hp_testimonial_banner(copy2_text1, copy2_text2, cta_text, user2_name,
                                                                   product_name)
                else:
                    print('Promotional banner')
                    return self.calc_desktop_hp_promotional_banner(copy2_text1, copy2_text2, cta_text, product_name)
            else:
                if testimonial:
                    print('Testimonial banner')
                    return self.calc_mobile_hp_testimonial_banner(copy_text1, copy_text2, copy_text3, copy_text4,
                                                                  cta_text, user_name, product_name)
                else:
                    print('Promotional banner')
                    return self.calc_mobile_hp_promotional_banner(copy2_text1, copy2_text2, cta_text, product_name)

        elif page_type == 'pp':
            # product page
            if not is_mobile:
                if testimonial:
                    print('Testimonial banner')
                    return self.calc_desktop_pp_testimonial_banner(copy_text1, copy_text2, user_name)
                else:
                    print('Promotional banner')
                    return self.calc_desktop_pp_promotional_banner(copy2_text1, copy2_text2)
            else:
                print('Promotional banner')
                return self.calc_mobile_pp_promotional_banner(copy2_text1, copy2_text2)

        elif page_type == 'cp':
            # cart page
            if not is_mobile:
                if testimonial:
                    print('Testimonial banner')
                    return self.calc_desktop_cp_testimonial_banner(copy_text1, copy_text2, user_name)
                else:
                    print('Promotional banner')
                    return self.calc_desktop_cp_promotional_banner(copy2_text1, copy2_text2)
            else:
                print('Promotional banner')
                return self.calc_mobile_cp_promotional_banner(copy2_text1, copy2_text2)
