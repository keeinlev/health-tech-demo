from django.test import TestCase, LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from pytz import timezone
from datetime import date, datetime, timedelta
from accounts.models import User, PatientInfo, DoctorInfo
from book.models import Appointment

# Create your tests here.
class BookTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome('C:\\bin\\chromedriver.exe')
        cls.selenium.implicitly_wait(5)
        new = User.objects.create(type='PATIENT', email='test@gmail.com', first_name='test', last_name='user', dob='2000-02-02', phone='0129438492')
        new2 = User.objects.create(type='DOCTOR', email='test2@gmail.com', first_name='test', last_name='doctor', dob='2000-02-02', phone='0129438493')
        new.set_password('asdfghjkl')
        new.save()
        new2.set_password('asdfghjkl')
        new2.save()
        cls.test_user = new
        cls.test_doctor = new2
        PatientInfo.objects.create(user=cls.test_user, ohip_number='9999-999-999-ZZ', ohip_expiry='2022-02-02')
        DoctorInfo.objects.create(user=cls.test_doctor, consultations='Fever, Cold, Aches', certification='Family M.D.', languages='English, French, Chinese')
        d = datetime.now() + timedelta(days=2)
        cls.test_appt = Appointment.objects.create(doctor=cls.test_doctor, date=str(d.date()), time=800, datetime=datetime(d.year, d.month, d.day, 8, 0).astimezone(timezone('America/New_York')))

    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def testbooking(self):
        selenium = self.selenium
        selenium.get('%s%s' % (self.live_server_url, '/accounts/login'))
        time.sleep(2)
        selenium.find_element_by_name('username').send_keys(self.test_user.email)
        selenium.find_element_by_name('password').send_keys('asdfghjkl')
        selenium.find_element_by_id('login-submit').click()
        print(f'{"Login":.<30}OK')
        time.sleep(2)
        selenium.get('%s%s' % (self.live_server_url, '/book'))
        print(f'{"GET Book Page":.<30}OK')
        selenium.find_element_by_name('next').click()
        time.sleep(2)
        selenium.find_elements_by_class_name('doctor-container')[0].click()
        selenium.execute_script(f'$("#bookcalendar").calendar("set date", "{str(self.test_appt.date)}");')
        #selenium.execute_script(f'document.getElementById("id_date").value = "{str(self.test_appt.date)}";')
        selenium.execute_script('console.log(document.getElementById("id_date").value);')
        selenium.find_element_by_id('booksubmit').click()
        assert len(Appointment.objects.all()) == 1
        assert Appointment.objects.last().patient == self.test_user
        assert Appointment.objects.last().consultation in self.test_doctor.userType.more.consultations
        assert not Appointment.objects.last().reminder_sent
        assert not Appointment.objects.last().ms_event_created
        assert Appointment.objects.last().booked
        print(f'{"POST Appointment":.<30}OK')
