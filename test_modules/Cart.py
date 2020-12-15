import platform
import unittest

import utilities.logger as ulogger
import utilities.parser as parser

from time import sleep
from price_parser import Price
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


class Cart(unittest.TestCase):
    # log = logger.Logger()

    logger = ulogger.Logger()
    logger.set_up()
    log = logger.get_logger()

    #############################
    ### CLASS SETUP FUNCTIONS ###
    #############################

    # Setup required prior to test case
    def setUp(self):
        options = Options()
        if platform.system() == 'Darwin':
            chromedriver_path = '../tools/chromedriver_mac'
            options.add_argument('--start-maximized')
        elif platform.system() == 'Linux':
            chromedriver_path = '../tools/chromedriver_linux'
            options.add_argument('--start-maximized')
        elif platform.system() == 'Windows':
            chromedriver_path = '../tools/chromedriver_win.exe'
            options.add_argument('--start-maximized')
        else:
            self.log.error('Unrecognized platform! ')
            return 'Unrecognized platform! '

        self.driver = webdriver.Chrome(chromedriver_path, options=options)
        self.log.info(f'Opening chromedriver for {str(platform.system())} and navigate to www.bitdefender.com')
        self.driver.get('https://www.bitdefender.com')

    # Closing test case
    def tearDown(self):
        self.log.info('Closing chromedriver')
        self.driver.quit()

    ####################################
    ### AUXILIARY / HELPER FUNCTIONS ###
    ####################################

    # close cookies badge
    def accept_cookies(self):
        path = parser.get_value('AcceptCookies')
        self.driver.find_element_by_xpath(path).click()

    # handle price and currency separate
    def parse_price(self, price):
        currency = Price.fromstring(price).currency
        if currency == '$':
            currency = 'USD'
        elif currency == '€':
            currency = 'EUR'
        elif currency == '£':
            currency = 'GBP'
        amount = Price.fromstring(price).amount_float
        return currency, amount

    # Adding "bitdefender premium security" product to cart, check
    # and save needed details for further validations
    def add_product_to_cart(self):
        self.accept_cookies()
        self.log.info('Navigating to Home -> See solutions')
        path = parser.get_value('SeeSolutions')
        self.driver.find_element_by_xpath(path).click()
        self.assertIn('solutions', self.driver.current_url)
        self.log.info('Clicking on Multiplatform')
        path = parser.get_value('MultiplatformButton')
        self.driver.find_element_by_id(path).click()
        sleep(2)
        path = parser.get_value('MultiplatformSelected')
        attr = self.driver.find_element_by_xpath(path).get_attribute("class")
        self.log.info('Check that Multiplatform was correctly selected')
        self.assertIn('active', attr)
        path = parser.get_value('PricePLP')
        price_plp = self.driver.find_element_by_xpath(path).text
        path = parser.get_value('ProductNamePLP')
        product_name_plp = self.driver.find_element_by_xpath(path).text
        currency_plp, amount_plp = self.parse_price(price_plp)
        product_plp = {
            'name': product_name_plp,
            'price': amount_plp,
            'currency': currency_plp
        }
        self.log.info('Checking selected product corresponds with the requirements')
        self.assertIn('premium security', product_plp['name'].lower())
        self.log.info('Adding product to cart')
        path = parser.get_value('BuyNowMP')
        self.driver.find_element_by_xpath(path).click()
        self.log.info('Check redirect to checkout')
        self.assertIn('/store.bitdefender.com/order/checkout.php', self.driver.current_url)
        return product_plp

    # Check and save needed details for further validations, in cart
    def get_product_from_cart(self):
        path = parser.get_value('ProductNameCart')
        product_name_cart = self.driver.find_element_by_xpath(path).text
        path = parser.get_value('PriceCart')
        price_cart = self.driver.find_element_by_xpath(path).text
        currency_cart, amount_cart = self.parse_price(price_cart)
        path = parser.get_value('CartTotal')
        total = self.driver.find_element_by_xpath(path).text
        _, amount_total = self.parse_price(total)
        product_cart = {
            'name': product_name_cart,
            'price': amount_cart,
            'currency': currency_cart,
            'total': amount_total
        }
        self.assertIn('premium security', product_cart['name'].lower())
        return product_cart

    # ensure same currency is used for accurate validation
    def change_currency(self, currency):
        path = parser.get_value('CurrencyCart')
        self.driver.find_element_by_xpath(path).click()
        path = path + '/option'
        currencies = self.driver.find_elements_by_xpath(path)
        for i in range(len(currencies)):
            if currencies[i].get_attribute('value') == currency:
                self.driver.find_element_by_xpath(path+f'[{str(i+1)}]').click()
                return

    # add more products to cart
    def update_quantity(self, new_qty):
        path = parser.get_value('QtyBox')
        qty_box = self.driver.find_element_by_id(path)
        current_qty = qty_box.get_attribute('value')
        self.assertEqual(int(current_qty), 1)
        qty_box.send_keys(Keys.BACKSPACE + str(new_qty))
        path = parser.get_value('UpdateButton')
        self.driver.find_element_by_xpath(path).click()
        return self.get_product_from_cart()

    def remove_product_from_cart(self):
        path = parser.get_value('RemoveFromCart')
        self.driver.find_element_by_id(path).click()
        sleep(3)

    ###########################
    ### TEST CASE FUNCTIONS ###
    ###########################

    # test-case 1: compare price PLP (product listing page) vs. cart
    def test_priceInCart(self):
        product_plp = self.add_product_to_cart()
        product_cart = self.get_product_from_cart()
        self.log.info('Validating price when default quantity is added to cart')
        checked = False
        if product_plp['currency'] == product_cart['currency']:
            try:
                self.assertEqual(product_plp['price'], product_cart['price'])
                checked = True
            except AssertionError:
                self.assertEqual(product_plp['price'], product_cart['total'])
                checked = True
        if not checked:
            self.log.info('Adjusting currency for valid check')
            self.change_currency(product_plp['currency'])
            product_cart = self.get_product_from_cart()
            try:
                self.assertEqual(product_plp['price'], product_cart['price'])
            except AssertionError:
                self.assertEqual(product_plp['price'], product_cart['total'])
        self.log.info('SUCCESS')

    # test-case 2: check price after increasing quantity
    def test_priceInUpdatedCart(self):
        self.add_product_to_cart()
        product_cart = self.get_product_from_cart()
        new_qty = 2
        cart_updated = self.update_quantity(new_qty)
        self.log.info('Validating price when quantity is updated to 2 units')
        try:
            self.assertEqual(product_cart['price'] * new_qty, cart_updated['price'])
        except AssertionError:
            self.assertEqual(product_cart['total'] * new_qty, cart_updated['total'])
        self.remove_product_from_cart()
        self.assertIn('solutions', self.driver.current_url)
        self.log.info('SUCCESS')

# unittest.main()