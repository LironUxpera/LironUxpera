class ClientData:
    def __init__(self, client):
        self.client = client

        self.dp_events = ['search', 'search_bar', 'Product_Viewed']
        self.bh_events = ['Clicked_Banner', 'promotions']
        self.nb_events = ['hp_banner_custom']
        self.sl_events = ['new_arrivals', 'best_sellers']
        self.sb_events = ['reviews', 'timeout', 'terms_and_cond', 'security_and_priv', 'about_us', 'browsing_no_click',
                          'Scrolling_To_Second_Part', 'scrolling_to_third']

        # load the behavior mapping, copy & cta tables
        self.behavior_mapping_df = None
        self.copy_df = None
        self.cta_df = None
        self._load_data_tables()

        # load the client banners
        self.desktop_promotional_banner = ''
        self.desktop_review_banner = ''
        self.mobile_promotional_banner = ''
        self.mobile_review_banner = ''
        self._load_banners()

    def _load_data_tables(self):
        pass

    def _load_banners(self):
        pass

    def calc_banner(self, assumed_behaviour):
        return None
