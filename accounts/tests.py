from django.test import TestCase, LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import date
from accounts.models import User

# Create your tests here.
regData = {'email1': '',
    'email2': '',
    'pw1': '',
    'pw2': '',
    'fn': '',
    'ln': '',
    'dob': '',
    'phone': '',
    'ohip': '',
    'ohipv': '',
    'ohipe': ''
}
class UserTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome('C:\\bin\\chromedriver.exe')
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def registrationHelper(self, data):
        selenium = self.selenium
        selenium.get('%s%s' % (self.live_server_url, '/accounts/register'))
        selenium.find_element_by_name('email1').send_keys(data['email1'])
        selenium.find_element_by_name('email2').send_keys(data['email2'])
        selenium.find_element_by_name('next1').click()
        time.sleep(2)
        selenium.find_element_by_name('password1').send_keys(data['pw1'])
        selenium.find_element_by_name('password2').send_keys(data['pw2'])
        selenium.find_element_by_name('next2').click()
        time.sleep(2)
        selenium.find_element_by_name('first_name').send_keys(data['fn'])
        selenium.find_element_by_name('last_name').send_keys(data['ln'])
        dobfield = selenium.find_element_by_name('dob')
        dobfield.click()
        dobfield.send_keys(Keys.CONTROL, "a")
        dobfield.send_keys(Keys.BACKSPACE)
        dobfield.send_keys(data['dob'])
        selenium.find_element_by_name('phone').send_keys(data['phone'])
        selenium.find_element_by_name('next3').click()
        time.sleep(2)
        selenium.find_element_by_name('ohip').send_keys(data['ohip'])
        selenium.find_element_by_name('ohip_version').send_keys(data['ohipv'])
        expiryfield = selenium.find_element_by_name('ohip_expiry')
        expiryfield.click()
        expiryfield.send_keys(Keys.CONTROL, "a")
        expiryfield.send_keys(Keys.BACKSPACE)
        expiryfield.send_keys(data['ohipe'])

    def testBadRegistration(self):
        User.objects.create(email='test@gmail.com')
        selenium = self.selenium
        regData = {'email1': 'test@gmail.com',
            'email2': 'test@gmail.com',
            'pw1': 'asdfghjkl',
            'pw2': 'asdfghjkl',
            'fn': 'test',
            'ln': 'user',
            'dob': '20000202',
            'phone': '1234567891',
            'ohip': '1234567891',
            'ohipv': 'GF',
            'ohipe': '20220202'
        }
        self.registrationHelper(regData)
        selenium.find_element_by_id('register-submit').click()
        assert self.live_server_url + '/accounts/register' == selenium.current_url and selenium.find_element_by_class_name('not-unique').get_attribute('innerHTML') == 'Email already registered to existing account!'

    def testSuccessfulRegistration(self):
        selenium = self.selenium
        regData = {'email1': 'test@gmail.com',
            'email2': 'test@gmail.com',
            'pw1': 'asdfghjkl',
            'pw2': 'asdfghjkl',
            'fn': 'test',
            'ln': 'user',
            'dob': '20000202',
            'phone': '1234567891',
            'ohip': '1234123123',
            'ohipv': 'GF',
            'ohipe': '20220202'
        }
        self.registrationHelper(regData)
        selenium.find_element_by_id('register-submit').click()
        time.sleep(2)
        print(selenium.current_url)
        assert self.live_server_url + '/accounts/need_activate' == selenium.current_url
        test_user = User.objects.last()
        assert test_user.type == 'PATIENT'
        assert test_user.first_name == 'test'
        assert test_user.last_name == 'user'
        assert test_user.email == 'test@gmail.com'
        assert test_user.phone == '1234567891'
        assert test_user.is_active == False
        assert test_user.dob == date(2000, 2, 2)
        assert test_user.userType.more.ohip_number == '1234-123-123-GF'
        assert test_user.userType.more.ohip_expiry == date(2022, 2, 2)

    def missingFieldHelper(self, data, field):
        selenium = self.selenium
        data[field] = ''
        print(data)
        self.registrationHelper(data)
        btndisabled = selenium.find_element_by_id('register-submit').get_property('disabled')
        print(btndisabled)
        assert btndisabled

    def testMissingFields(self):
        regData = {'email1': 'test@gmail.com',
            'email2': 'test@gmail.com',
            'pw1': 'asdfghjkl',
            'pw2': 'asdfghjkl',
            'fn': 'test',
            'ln': 'user',
            'dob': '20000202',
            'phone': '1234567891',
            'ohip': '1234123123',
            'ohipv': 'GF',
            'ohipe': '20220202'
        }
        for k in regData.keys():
            self.missingFieldHelper(regData.copy(), k)

    