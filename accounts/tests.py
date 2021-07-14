from django.test import TestCase, LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import date
from accounts.models import User, PatientInfo

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

    def untestBadRegistration(self):
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
        assert self.live_server_url + '/accounts/register' == selenium.current_url and selenium.find_element_by_class_name('not-unique').get_attribute('innerHTML') == 'Email already registered to existing account!'
        selenium.find_element_by_id('register-submit').click()
        assert self.live_server_url + '/accounts/register' == selenium.current_url and 'Error code 500' in selenium.find_element_by_id('alert-message')
        print(f'{"Existing Email":.<30}OK')

    def untestSuccessfulRegistration(self):
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
        assert test_user.userType.more.dob == date(2000, 2, 2)
        assert test_user.userType.more.ohip_number == '1234-123-123-GF'
        assert test_user.userType.more.ohip_expiry == date(2022, 2, 2)
        print(f'{"Successful Registration":.<30}OK')


    def missingFieldHelper(self, data, field):
        selenium = self.selenium
        data[field] = ''
        print(data)
        self.registrationHelper(data)
        btndisabled = selenium.find_element_by_id('register-submit').get_property('disabled')
        print(btndisabled)
        assert btndisabled
        print(f'Missing {field:.<30}OK')

    def untestMissingFields(self):
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

    def untestUserFunctions(self):
        new = User.objects.create(type='PATIENT', email='test@gmail.com', first_name='test', last_name='user', phone='1239393921')
        new.set_password('asdfghjkl')
        new.save()
        PatientInfo.objects.create(user=new, ohip_number="4321-123-123-HJ", ohip_expiry="2022-02-02", dob='2000-02-02')
        selenium = self.selenium
        selenium.get('%s%s' % (self.live_server_url, '/accounts/login'))
        time.sleep(2)
        selenium.find_element_by_name('username').send_keys(new.email)
        selenium.find_element_by_name('password').send_keys('asdfghjkl')
        selenium.find_element_by_id('login-submit').click()
        assert self.live_server_url + '/' == selenium.current_url
        print(f'{"Login":.<30}OK')
        selenium.get('%s%s' % (self.live_server_url, '/accounts/editprofile'))
        time.sleep(2)
        assert selenium.find_element_by_name('first_name').get_attribute('value') == new.first_name
        assert selenium.find_element_by_name('last_name').get_attribute('value') == new.last_name
        assert selenium.find_element_by_name('dob').get_attribute('value') == str(new.dob)
        assert selenium.find_element_by_name('phone1').get_attribute('value') + selenium.find_element_by_name('phone2').get_attribute('value') + selenium.find_element_by_name('phone3').get_attribute('value') == new.phone
        assert selenium.find_element_by_name('ohip1').get_attribute('value') + '-' + selenium.find_element_by_name('ohip2').get_attribute('value') + '-' + selenium.find_element_by_name('ohip3').get_attribute('value') + '-' + selenium.find_element_by_name('ohip_version').get_attribute('value')  == new.userType.more.ohip_number
        assert selenium.find_element_by_name('ohip_expiry').get_attribute('value') == str(new.userType.more.ohip_expiry)
        print(f'{"GET Edit Profile":.<30}OK')
