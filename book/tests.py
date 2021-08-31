from django.test import TestCase, LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from pytz import timezone
from datetime import date, datetime, timedelta
from accounts.models import User, PatientInfo, DoctorInfo
from book.models import Appointment
from book.views import getDateTime, fromisoform, generateMeetingId
from health.settings import MS_TEAMS_MEETING_ID_LENGTH
from health.colors import color

eastern = timezone('America/New_York')

allChars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNNM1234567890"

# Create your tests here.
class BookTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome('C:\\bin\\chromedriver.exe')
        cls.selenium.implicitly_wait(5)
        new = User.objects.create(type='PATIENT', email='test@gmail.com', first_name='test', last_name='user', phone='0129438492')
        new2 = User.objects.create(type='DOCTOR', email='test2@gmail.com', first_name='test', last_name='doctor', phone='0129438493')
        new.set_password('asdfghjkl')
        new.save()
        new2.set_password('asdfghjkl')
        new2.save()
        cls.test_user = new
        cls.test_doctor = new2
        PatientInfo.objects.create(user=cls.test_user, ohip_number='9999-999-999-ZZ', dob='2000-02-02', ohip_expiry='2022-02-02')
        DoctorInfo.objects.create(user=cls.test_doctor, consultations='Fever, Cold, Aches', certification='Family M.D.', languages='English, French, Chinese')
        d = datetime.now() + timedelta(days=2)
        cls.test_appt = Appointment.objects.create(doctor=cls.test_doctor, date=str(d.date()), time=800, datetime=datetime(d.year, d.month, d.day, 8, 0).astimezone(eastern))

    
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
        print(f'{color.GREEN}{"Login":.<30}OK{color.END}')
        time.sleep(2)
        selenium.get('%s%s' % (self.live_server_url, '/book'))
        print(f'{color.GREEN}{"GET Book Page":.<30}OK{color.END}')
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
        print(f'{color.GREEN}{"POST Appointment":.<30}OK{color.END}')

class AppointmentTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        new = User.objects.create(type='PATIENT', email='test3@gmail.com', first_name='test', last_name='user', phone='0129438492')
        new2 = User.objects.create(type='DOCTOR', email='test4@gmail.com', first_name='test', last_name='doctor', phone='0129438493')
        new.set_password('asdfghjkl')
        new.save()
        new2.set_password('asdfghjkl')
        new2.save()
        cls.test_user = new
        cls.test_doctor = new2
        PatientInfo.objects.create(user=cls.test_user, ohip_number='9999-999-999-XX', dob='2000-02-02', ohip_expiry='2022-02-02')
        DoctorInfo.objects.create(user=cls.test_doctor, consultations='Fever, Cold, Aches', certification='Family M.D.', languages='English, French, Chinese')

    def testAppointmentBasic(self):
        a = Appointment.objects.create(doctor=self.test_doctor, date="2021-07-09", time=800, datetime=datetime(2021, 7, 9, 8, 0).astimezone(eastern))
        assert a.ms_event_created == False
        assert a.reminder_sent == 0
        assert a.type == None
        assert a.meeting_id == None
        assert a.patient == None
        assert a.booked == False
        assert a.consultation == None
        print(f'{color.GREEN}{"Basic Appt Creation":.<30}OK{color.END}')
    
class BookHelperTests(TestCase):
    def testGenerateMeetingId(self):
        trials = 10
        for i in range(1, trials + 1):
            print(f'{color.BLUE}GenerateMeetingId Test Trial {i}{color.END}')
            test_id = generateMeetingId()
            assert len(test_id) == MS_TEAMS_MEETING_ID_LENGTH
            print(f'{color.GREEN}{"Meeting ID Length":.<30}OK{color.END}')
            for c in test_id:
                assert c in allChars
            print(f'{color.GREEN}{"Meeting ID Chars":.<30}OK{color.END}')
    
    def testGetDateTime(self):
        return
