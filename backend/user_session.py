from urllib.parse import urlparse
from user import User
from send_command import SendCommand

command_sender = SendCommand()


class UserSession:
    def __init__(self, client, uuid, client_data):
        self.client = client
        self.uuid = uuid
        self.client_data = client_data
        self.last_page = ''  # last page this user is on - used for banner display
        self.page_type = ''

        self.user = User(self.client, self.uuid)

    def calc_page_type(self):
        page = urlparse(self.last_page)
        page = page.path

        print('Calculating page for: ', page)

        if 'checkout/cart/' in page:
            return 'cp'

        if page == '' or page == 'en/':
            return 'hp'

        if 'product/view/' in page:
            return 'pp'

        # TODO we do not recognize non obvious product pages

        return ''

        # hp
        # https://prmusa.prmstaging.com/en/
        # https://prmusa.prmstaging.com/
        # https://www.premierdeadsea-usa.com/en/

        # pp
        # https://prmusa.prmstaging.com/en/minerals-to-go-active-nourishing-facial-mask
        # https://prmusa.prmstaging.com/en/catalog/product/view/id/1387/s/trio-elite/category/107/
        # https://prmusa.prmstaging.com/en/catalog/product/view/id/1423/s/lovely-body-gift-set/category/29/
        # https://prmusa.prmstaging.com/en/prestige-skincare/collection/refining/prestige-miracle-noir-mask

        # cp
        # https://prmusa.prmstaging.com/en/checkout/cart/

        # other
        # https://prmusa.prmstaging.com/en/classic-skincare/category
        # https://prmusa.prmstaging.com/en/prestige-skincare/collection/refining
        # https://prmusa.prmstaging.com/en/classic-skincare/benefits
        # https://prmusa.prmstaging.com/the-dead-sea
        # https://prmusa.prmstaging.com/about-us

    def add_event(self, event):
        print('UserSession Add event')
        self.user.add_event(event)
        self.last_page = event.page
        self.page_type = self.calc_page_type()
        print('On page type: ', self.page_type)

        # temp for testing - if we are on staging and on a page we can show a banner
        if self.client == 'premier_staging' and self.page_type != '':
            self.replace_generic_banner('SB', self.page_type, self.user.get_is_mobile())

        # if not self.user.get_replaced_generic_banner():
        #     behaviour = self.client_data.check_behaviour(self.user)
        #     if behaviour is not None:
        #         print(f'== Calculated Behaviour = {behaviour}')
        #         self.user.set_behaviour(behaviour)
        #         self.replace_generic_banner(behaviour)

        # save updates to user
        print('Save User: ', self.user.save_user())

    def replace_generic_banner(self, assumed_behaviour, page_type, is_mobile):
        html = self.client_data.calc_banner(assumed_behaviour, page_type, is_mobile)
        command_sender.push_banner_to_user(self.client, self.uuid, str(html), self.last_page)
        self.user.set_replaced_generic_banner()
