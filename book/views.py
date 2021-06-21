from django.shortcuts import render, redirect
from .forms import CreateAppointmentForm, CreateAppointmentRangeForm, CancelAppointmentRangeForm, EditAppointmentForm, CancelConfirmForm
from accounts.models import User, Doctor, DoctorInfo, Patient, PatientInfo
from .models import Appointment
from appointment.models import ApptDetails
from django.http import HttpResponse, JsonResponse
from .times import IntTimes
from datetime import date, datetime, timedelta
from .tasks import send_reminder
from django.core.mail import send_mail
from django.urls import reverse
from pytz import timezone, utc
from health.settings import MS_TEAMS_MEETING_URL_1 as meeting_url_1, MS_TEAMS_MEETING_URL_2 as meeting_url_2, MS_TEAMS_MEETING_ID_LENGTH as meeting_id_length, SMS_CARRIER
from random import choice
from string import ascii_letters, digits, punctuation
from django.db import IntegrityError
from graph.graph_helper import create_event
from graph.auth_helper import get_token
import asyncio
from book.tasks import emailWrapper, SMSWrapper

eastern = timezone('America/New_York')

allChars = ascii_letters + digits + digits

# Returns a random character to serve as a meeting_id
def generateMeetingId():
    return ''.join(choice(allChars) for i in range(meeting_id_length))

# Helper function that breaks down an ISO formatted date string into a tuple of integer values
# Example: '2021-06-16' -> (2021, 6, 16)
def fromisoform(d):
    year = int(d[:4])
    month = int(d[5:7])
    day = int(d[8:10])
    return (year, month, day)

# Helper function that takes in a datetime date and an integer representation of a time and returns it as a full datetime object in UTC
# Example: (datetime.date(2021, 6, 16), 800) -> datetime.datetime(2021, 6, 16, 12, 0, 0)
def getDateTime(date, time):
    non_loc = datetime(date.year, date.month, date.day, time // 100, time % 100).astimezone(utc)
    return non_loc


# Create your views here.

# View for Doctor Dashboard
def doctordashboard(request):
    u = request.user
    if u.is_authenticated:
        if u.type == "DOCTOR":

            # Forms for creating a single time slot opening, a range of time slots and cancelling a range of time slots
            single_appt_form = CreateAppointmentForm(initial={'doctor':u.pk})
            mult_appt_form = CreateAppointmentRangeForm()
            cancel_mult_form = CancelAppointmentRangeForm()
            if (request.method == "GET"):
                return render(request, 'doctordashboard.html', {'doctor': Doctor.objects.get(pk=u.pk), 'cancel_mult_form': cancel_mult_form, 'single_appt_form': single_appt_form, 'mult_appt_form': mult_appt_form })
    return render(request, 'doctordashboard.html')

# Redirect view right after creating an appointment to prevent unexpected form resubmissions
def apptcreated(request):
    u=request.user
    if u.is_authenticated:
        if u.type == "DOCTOR":
            single_appt_form = CreateAppointmentForm(initial={'doctor':u.pk})
            mult_appt_form = CreateAppointmentRangeForm()
            cancel_mult_form = CancelAppointmentRangeForm()
            if (request.method == "GET"):
                message = "Appointment slot(s) created!"
                return render(request, 'doctordashboard.html', {'doctor': Doctor.objects.get(pk=u.pk), 'cancel_mult_form': cancel_mult_form, 'single_appt_form': single_appt_form, 'mult_appt_form': mult_appt_form, 'message':message})
    return render(request, 'doctordashboard.html')

# View for Doctor opening an Appointment time slot
def booksingle(request):
    u=request.user
    if u.is_authenticated:
        if u.type == "DOCTOR":
            if (request.method == "POST"):
                form = CreateAppointmentForm(request.POST)
                print(request.POST)
                if form.is_valid():

                    # Uses model form to create object
                    appt = form.save(commit=False)
                    appt.doctor = u
                    appt.datetime = getDateTime(form.cleaned_data['date'], int(form.cleaned_data['time']))
                    appt.save()

                    # Creates the corresponding Appointment Details object
                    ps = ApptDetails.objects.create(date=appt.date, appt=appt)
                    return redirect('apptcreated')
                else:
                    return redirect('doctordashboard')
    return render(request, 'doctordashboard.html')

# View for Doctor opening a range of Appointment time slots
def bookmult(request):
    u=request.user
    if u.is_authenticated:
        if u.type == "DOCTOR":
            if (request.method == "POST"):
                form = CreateAppointmentRangeForm(request.POST)
                if form.is_valid():

                    # Getting start and end date/time ranges
                    startdate = fromisoform(request.POST['startdate'])
                    startdate = date(startdate[0], startdate[1], startdate[2])
                    starttime = request.POST['starttime']
                    enddate = fromisoform(request.POST['enddate'])
                    enddate = date(enddate[0], enddate[1], enddate[2])
                    endtime = request.POST['endtime']
                    d = startdate
                    while(d <= enddate):

                        # Gets the list of all time integer values
                        timeKeys = IntTimes.getKeys()
                            
                        # Creates an Appointment for every time in the range and for every day in the range
                        for i in range(timeKeys.index(starttime), timeKeys.index(endtime) + 1):
                            t = timeKeys[i]
                            
                            # Create only if it does not exist yet
                            if not (Appointment.objects.filter(doctor = u, date = str(d), time = t).exists()):
                                a = Appointment.objects.create(doctor = u, date = str(d), time = t, datetime=getDateTime(d, int(t)))
                                ApptDetails.objects.create(appt=a, date=a.date)

                        # Day increment
                        d += timedelta(days=1)

                    return redirect('apptcreated')
                else:
                    return render(request, 'doctordashboard.html', {'message': 'Oops! An error occurred.', 'doctor': Doctor.objects.get(pk=u.pk), 'cancel_mult_form': CancelAppointmentRangeForm(), 'single_appt_form': CreateAppointmentForm(initial={'doctor':u.pk}), 'mult_appt_form': CreateAppointmentRangeForm() })
        else:
            pass
    return render(request, 'doctordashboard.html')

# View for closing a range of open Appointment time slots
def cancelmult(request):
    u=request.user
    if u.is_authenticated:
        if u.type == "DOCTOR":
            if (request.method == "POST"):
                form = CancelAppointmentRangeForm(request.POST)
                if form.is_valid():

                    # Uses same method as creation
                    startdate = fromisoform(request.POST['c_startdate'])
                    startdate = date(startdate[0], startdate[1], startdate[2])
                    starttime = request.POST['c_starttime']
                    enddate = fromisoform(request.POST['c_enddate'])
                    enddate = date(enddate[0], enddate[1], enddate[2])
                    endtime = request.POST['c_endtime']
                    d = startdate
                    while(d <= enddate):
                        timeKeys = IntTimes.getKeys()
                        for i in range(timeKeys.index(starttime), timeKeys.index(endtime) + 1):
                            t = timeKeys[i]
                            appts = Appointment.objects.filter(doctor = u, date = str(d), time = t, booked=False)
                            if (appts.exists()):
                                appts.first().delete()
                        d += timedelta(days=1)
                    return redirect('apptcanceled')
                else:
                    return render(request, 'doctordashboard.html', {'message': 'Oops! An error occurred.', 'doctor': Doctor.objects.get(pk=u.pk), 'cancel_mult_form': CancelAppointmentRangeForm(), 'single_appt_form': CreateAppointmentForm(initial={'doctor':u.pk}), 'mult_appt_form': CreateAppointmentRangeForm() })
        else:
            pass
    return render(request, 'doctordashboard.html')

# View for handling AJAX request during Doctor time slot scheduling, will make sure end date selection only includes times after selected start date.
# See docdash.js line 34
def updateenddate(request):
    u = request.user
    if (u.is_authenticated):
        if u.type == "DOCTOR":
            starttime = None
            is_cancel = 0
            if (not request.GET.get('starttime', None)):
                starttime = request.GET.get('c_starttime', None)
                is_cancel = 1
            else:
                starttime = request.GET.get('starttime', None)
            possibletimes = list(filter(lambda time: time[0] >= int(starttime), IntTimes.choices))
            keys=[]
            values=[]
            for time in possibletimes:
                keys.append(time[0])
                values.append(time[1])
            data = {
                'keys': keys,
                'values': values,
                'is_cancel': is_cancel
            }
            return JsonResponse(data)
    return JsonResponse({})

# View for AJAX request fetching details for all Appointments on a selected date, updating Appointment table on dashboard
# See docdash.js line 126
def getdates(request):
    u = request.user
    if (u.is_authenticated):
        if u.type == "DOCTOR":
            date = request.GET.get('date', None)
            appts = []
            for a in u.getAppts.filter(date=date):
                dt = a.datetime.astimezone(timezone('America/New_York'))
                appts.append({
                    'date': str(a.date),
                    'time': f'{dt.hour % 12 if dt.hour % 12 else 12}:{"0" if dt.minute < 10 else ""}{dt.minute}{"PM" if dt.hour > 11 else "AM"}',
                    'booked': "<b style='color:" + ("red'>Booked" if a.booked else "green'>Available") + "</b>",
                    'patient': f'{a.patient.first_name} {a.patient.last_name}' if a.patient else "None",
                    'detailsurl': reverse('details', kwargs={'pk': a.pk}),
                })
            data = {'apptdata': appts}
            return JsonResponse(data)
    return JsonResponse({})

# View for AJAX request fetching details for all Appointments on a selected date and scheduled for a searched Patient, updating Appointment table on dashboard
# See docdash.js line 88
def patientsearch(request):
    u = request.user
    if (u.is_authenticated):
        if u.type == "DOCTOR":
            searched = request.GET.get('patient-search')
            date = request.GET.get('date', None)

            # Using searched keyword, get Appointments where Patient first, preferred or last name matches
            # Will query all Appointments if no date is given
            query = u.getAppts.filter(patient__first_name__contains=searched) | u.getAppts.filter(patient__preferred_name__contains=searched) | u.getAppts.filter(patient__last_name__contains=searched)
            
            # Narrows query to match date
            if date != '0':
                query = u.getAppts.filter(date=date, patient__first_name__contains=searched) | u.getAppts.filter(date=date, patient__preferred_name__contains=searched) | u.getAppts.filter(date=date, patient__last_name__contains=searched)
            appts = []
            for a in query:
                dt = a.datetime.astimezone(timezone('America/New_York'))
                appts.append({
                    'date': str(a.date),
                    'time': f'{dt.hour % 12 if dt.hour % 12 else 12}:{"0" if dt.minute < 10 else ""}{dt.minute}{"PM" if dt.hour > 11 else "AM"}',
                    'booked': "<b style='color:" + ("red'>Booked" if a.booked else "green'>Available") + "</b>",
                    'patient': f'{a.patient.first_name} {a.patient.last_name}' if a.patient else "None",
                    'detailsurl': reverse('details', kwargs={'pk': a.pk}),
                })
            data = {'apptdata': appts}
            return JsonResponse(data)
    return JsonResponse({})

# View for AJAX request to check if a selected date and time has already been booked or not, used when Doctor opens a single time slot using calendar UI.
# See docdash.js line 155
def checkifbooked(request):
    u = request.user
    if (u.is_authenticated):
        if u.type == "DOCTOR":
            date = request.GET.get('date', None)
            time = request.GET.get('time', None)
            if date:
                data = {
                    'booked': Appointment.objects.filter(doctor=request.user, date=date, time=time).exists(),
                    'valid' : True
                }
                if data['booked']:
                    data['message'] = "This Appointment slot is already booked!"
                else:
                    data['message'] = "This Appointment slot is open!"
                return JsonResponse(data)
            else:
                data = {
                    'booked': False,
                    'valid': False,
                    'message': "Please select a date from the calendar."
                }
                return JsonResponse(data)
    return JsonResponse({})

# View for cancelling a single Appointment, booked or unbooked
def cancelappt(request, pk):
    u = request.user
    if u.is_authenticated:
        a = Appointment.objects.filter(pk=pk)
        if a.exists():
            a = a.first()
            if request.method == "POST":
                
                # A confirm cancel form will only show up in the GET request if the Appointment is booked
                form = CancelConfirmForm(request.POST)
                if form.is_valid():
                    target = a.doctor
                    other = f'Patient {a.patient}'
                    if u.type == "DOCTOR":
                        target = a.patient
                        other = f'Dr. {a.doctor}'
                    r = form.cleaned_data['reason']
                    
                    # Sends other party an SMS and Email message to notify them of cancellation
                    send_mail(
                        ''
                        'Hi, ' + target.first_name + '. Your appointment with ' + other + ' on ' + a.shortDateTime() + ' has been cancelled due to: ' + r + ('.\nPlease rebook for another time.' if target.type == 'PATIENT' else ''),
                        'healthapptdemo@gmail.com',
                        [target.phone + SMS_CARRIER],
                    )
                    send_mail(
                        'Your Appointment has been Cancelled',
                        'Hi,' + target.first_name + '\n\nWe are sorry to inform you that your appointment with ' + other + ' on ' + a.dateTime + ' has been cancelled for reason:\n' + r + ('\nPlease rebook an appointment for another time.\n' if target.type == 'PATIENT' else '') + '\nWe are sorry for the inconvenience.',
                        'healthapptdemo@gmail.com',
                        [target.email],
                    )
                    a.delete()
                    return redirect('apptcanceled')
            else:
                if a.booked:
                    # Only creates a confirmation form if Appointment is booked
                    form = CancelConfirmForm(initial={
                        'doctor': a.doctor,
                        'patient': a.patient,
                        'date': a.date,
                        'time': a.time,
                    })
                    return render(request, 'confirmcancel.html', { 'appt': a , 'form': form, 'dt': a.dateTime })
                else:
                    # If not booked, just delete the Appointment
                    a.delete()
                    return redirect('apptcanceled')
        else:
            return render(request, 'alert.html', {'message': 'Appointment does not exist!'})
    return render(request, 'doctordashboard.html')

# Redirect view once an Appointment has been cancelled to prevent unwanted form resubmissions
def apptcanceled(request):
    u=request.user
    if u.is_authenticated:
        if u.type == "DOCTOR":
            single_appt_form = CreateAppointmentForm(initial={'doctor':u.pk})
            mult_appt_form = CreateAppointmentRangeForm()
            cancel_mult_form = CancelAppointmentRangeForm()
            if (request.method == "GET"):
                message = "Appointment(s) cancelled."
                return render(request, 'doctordashboard.html', {'doctor': Doctor.objects.get(pk=u.pk), 'cancel_mult_form': cancel_mult_form, 'single_appt_form': single_appt_form, 'mult_appt_form': mult_appt_form, 'message':message})
        else:
            return render(request, 'index.html', {'message': 'Appointment Cancelled'})
    
    return render(request, 'doctordashboard.html')

# View for AJAX request to only show available date ranges for a selected Doctor with open time slots for Patient booking calendar
# See bookmethods.js line 5
def update_calendar(request):
    u = request.user
    if (u.is_authenticated):
        if u.type == "PATIENT":
            datesList = []
            consultations = []
            doctor_id = request.GET.get('doctor-id', None)
            d = Doctor.objects.filter(pk = doctor_id).first()
            for c in d.more.consultations.split(', '):
                consultations.append(c)
            for appt in Appointment.objects.filter(doctor = d, datetime__gt = datetime.now().astimezone(utc), booked=False).order_by('date', 'time'):
                if appt.date not in datesList:
                    datesList.append(appt.date)
            if len(datesList) == 1:
                datesList.append(datesList[0] + timedelta(days=1))
            data = {
                'apptdates': datesList,
                'consultations': consultations,
                'd_id': doctor_id
            }
            return JsonResponse(data)
    return JsonResponse({})

# View for Patient-side booking
def book(request):
    u = request.user
    if (u.is_authenticated):
        if u.type == "PATIENT":
            form = EditAppointmentForm()
            if (request.method == "POST"):
                form = EditAppointmentForm(request.POST)
                if form.is_valid():
                    appt_type = form.cleaned_data['appt_type']
                    doc = form.cleaned_data['doctor']
                    pat = u
                    date = form.cleaned_data['date']
                    time = form.cleaned_data['time']
                    consultation = form.cleaned_data['consultation']
                    meeting_id = generateMeetingId()
                    a = Appointment.objects.filter(doctor=doc, date=date, time=time, booked=False)

                    # Catching case where Patient tries to book a time slot they have already booked
                    if Appointment.objects.filter(patient=pat, date=date, time=time).exists():
                        error = 'You have already booked an appointment for this day and time.'
                        return render(request, 'book.html', { 'error_message': error, 'doctors': Doctor.objects.all(), 'doctorsinfo': DoctorInfo.objects.all(), 'form': form })
                    elif a.exists():
                        a = a.first()
                        a.patient = pat
                        a.consultation = consultation
                        a.type = appt_type
                        a.booked = True
                        a.save()

                        # Generation of unique meeting_id
                        while(1):
                            try:
                                a.meeting_id = meeting_id
                                a.save()
                                break
                            except IntegrityError as e:
                                print(e + ', trying new meeting_id')
                                meeting_id = generateMeetingId()

                        # If Patient is logged in with MS, will create a third-party Calendar event and update Appointment ms_event_created field
                        if u.ms_authenticated:
                            start = a.datetime.astimezone(eastern)
                            end = start + timedelta(minutes=15)
                            start = start.strftime('%Y-%m-%dT%H:%M')
                            end = end.strftime('%Y-%m-%dT%H:%M')
                            meeting_url = meeting_url_1 + a.meeting_id + meeting_url_2
                            body = "Please join the meeting at this link: " + meeting_url
                            create_event(get_token(request), f'Appointment with Dr. { a.doctor }', start, end, [a.doctor.email], body, 'Eastern Standard Time')
                            a.ms_event_created = True
                            a.save()

                        # Sends both parties a confirmation Email and SMS
                        asyncio.run(send_reminder(a.id, 'confirm'))

                        return redirect('booksuccess')
                    else:
                        error = 'The Appointment you tried to book either does not exist or has already been booked.'
                        return render(request, 'book.html', { 'error_message': error, 'doctors': Doctor.objects.all(), 'doctorsinfo': DoctorInfo.objects.all(), 'form': form })
                else:
                    return render(request, 'book.html', {'form': form, 'doctors': Doctor.objects.all(), 'doctorsinfo': DoctorInfo.objects.all()})
            else:
                return render(request, 'book.html', {'form': form, 'doctors': Doctor.objects.all(), 'doctorsinfo': DoctorInfo.objects.all()})
    return render(request, 'book.html')

# Redirect view for successfully booking Appointment to prevent unwanted form resubmissions
def booksuccess(request):
    u=request.user
    if u.is_authenticated:
        if u.type == "PATIENT":
            form = EditAppointmentForm()
            if (request.method == "GET"):
                message = "Appointment Booked."
                return render(request, 'book.html', {'form': form, 'doctors': Doctor.objects.all(), 'doctorsinfo': DoctorInfo.objects.all(), 'message':message})
    return render(request, 'book.html')

# View for AJAX request to fetch available times on a valid selected date when Patient is booking
# See bookmethods.js line 55
def findtimes(request):
    u = request.user
    if (u.is_authenticated):
        if u.type == "PATIENT":
            d = request.GET.get('doctor-id')
            date = request.GET.get('date')
            appts = Appointment.objects.filter(doctor = d, datetime__gt = datetime.now().astimezone(utc), date=date, booked=False).order_by('time')
            data = {}
            if (appts.exists()):
                values=[]
                keys=[]
                for appt in appts:
                    keys.append(appt.time)

                for time in list(filter(lambda tup: tup[0] in keys, IntTimes.choices)):
                    values.append(time[1])
                
                data = {
                    'keys': keys,
                    'values': values,
                }
            else:
                data['message'] = "No available appointment slots this day."
            
            return JsonResponse(data)
    return JsonResponse({})