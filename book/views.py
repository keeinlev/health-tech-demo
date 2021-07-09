from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.urls import reverse
from django.db import IntegrityError

from health.settings import MS_TEAMS_MEETING_URL_1 as meeting_url_1, MS_TEAMS_MEETING_URL_2 as meeting_url_2, MS_TEAMS_MEETING_ID_LENGTH as meeting_id_length, SMS_CARRIER, SIGNALWIRE_NUMBER, SIGNALWIRE_CLIENT as swclient

from .forms import CreateAppointmentForm, CreateAppointmentRangeForm, CancelAppointmentRangeForm, EditAppointmentForm, CancelConfirmForm
from .models import Appointment
from .times import IntTimes
from .tasks import send_reminder, emailWrapper

from accounts.models import User, Doctor, DoctorInfo, Patient, PatientInfo

from appointment.models import ApptDetails

from pytz import timezone, utc

from random import choice
from string import ascii_letters, digits, punctuation
from datetime import date, datetime, timedelta

from graph.graph_helper import create_event
from graph.auth_helper import get_token

import xlwt

from pprint import pprint

from asgiref.sync import sync_to_async, async_to_sync
import asyncio

eastern = timezone('America/New_York')

allChars = ascii_letters + digits + digits

# Asyncio Task for sending email
async def async_send_mail(subject, body, to):
    emailWrapper(subject, body, to=[to])

# Asynchronously sends multiple cancellation emails
async def send_cancellations(appts, reason):
    loop = asyncio.get_event_loop()
    tasks = [async_send_mail(
        'Your Appointment has been Cancelled',
        'Hi,' + appt.patient.first_name + '\n\nWe are sorry to inform you that your appointment with Dr. ' + str(appt.doctor) + ' on ' + appt.dateTime + ' has been cancelled for reason:\n' + reason + '\nPlease rebook an appointment for another time.\n\nWe are sorry for the inconvenience.',
        to=appt.patient.email)
        for appt in appts]
    print(tasks)
    for t in tasks:
        await t

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
    localTimeZone = datetime.now(utc).astimezone().tzinfo
    timezoneDifference = localTimeZone.utcoffset(datetime.now()) - timedelta(days=-1, seconds=72000)
    print(timezoneDifference)
    non_loc = datetime(date.year, date.month, date.day, time // 100, time % 100).astimezone(eastern) + timezoneDifference
    return non_loc


# Create your views here.

# View for Doctor Dashboard
@login_required
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

@login_required
def downloadApptHistory(request):
    u=request.user
    if u.is_authenticated:
        if u.type == 'DOCTOR':
            appts = Appointment.objects.filter(doctor=u, booked=True, datetime__lt=datetime.now().astimezone(utc))
            
            # content-type of response
            response = HttpResponse(content_type='application/ms-excel')

            #decide file name
            response['Content-Disposition'] = 'attachment; filename="djangoExcelTest.xls"'

            #creating workbook
            wb = xlwt.Workbook(encoding='utf-8')

            #adding sheet
            ws = wb.add_sheet("sheet1")

            # Sheet header, first row
            row_num = 0

            font_style = xlwt.XFStyle()
            # headers are bold
            font_style.font.bold = True

            #column header names, you can use your own headers here
            columns = ['Date', 'Time', 'Consultation', 'Patient Name', 'Patient DOB', 'Patient Address', 'Patient Email', 'Patient Phone #', 'Patient OHIP', 'Patient OHIP Expiry', 'Patient Pharmacy', 'Doctor Notes', 'Prescription']

            #write column headers in sheet
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)

            # Sheet body, remaining rows
            font_style = xlwt.XFStyle()

            #get your data, from database or from a text file...
            for appt in appts:
                row_num += 1
                print(appt.date)
                ws.write(row_num, 0, str(appt.date), font_style)
                ws.write(row_num, 1, dict(IntTimes.choices)[appt.time], font_style)
                ws.write(row_num, 2, appt.consultation, font_style)
                ws.write(row_num, 3, str(appt.patient), font_style)
                ws.write(row_num, 4, str(appt.patient.dob), font_style)
                ws.write(row_num, 5, f'{appt.patient.more.address}, {appt.patient.more.postal_code}', font_style)
                ws.write(row_num, 6, appt.patient.email, font_style)
                ws.write(row_num, 7, appt.patient.phone, font_style)
                ws.write(row_num, 8, appt.patient.more.ohip_number, font_style)
                ws.write(row_num, 9, str(appt.patient.more.ohip_expiry), font_style)
                ws.write(row_num, 10, appt.patient.more.pharmacy, font_style)
                ws.write(row_num, 11, ApptDetails.objects.get(appt=appt).notes, font_style)
                ws.write(row_num, 12, ApptDetails.objects.get(appt=appt).prescription, font_style)

            wb.save(response)
            return response


# Redirect view right after creating an appointment to prevent unexpected form resubmissions
@login_required
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
@login_required
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
@login_required
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

# AJAX handler for seeing if a selected range of Appointment time slots to be cancelled needs a reason (is booked and needs to notify Patient)
@login_required
def showreasontextbox(request):
    u=request.user
    if u.is_authenticated:
        if u.type == 'DOCTOR':
            startdate = fromisoform(request.GET.get('c_startdate', None))
            startdate = date(startdate[0], startdate[1], startdate[2])
            starttime = int(request.GET.get('c_starttime', None))
            enddate = fromisoform(request.GET.get('c_enddate', None))
            enddate = date(enddate[0], enddate[1], enddate[2])
            endtime = int(request.GET.get('c_endtime', None))
            if startdate and enddate and starttime and endtime:
                booked = Appointment.objects.filter(doctor=u, datetime__gte=getDateTime(startdate, starttime), datetime__lte=getDateTime(enddate, endtime), time__gte=starttime, time__lte=endtime, booked=True)
                if booked.exists():
                    return JsonResponse({'needs_reason':1})
                else:
                    return JsonResponse({'needs_reason':0})
    return JsonResponse({})

# View for closing a range of open Appointment time slots
@sync_to_async
@login_required
@async_to_sync
async def cancelmult(request):
    u=request.user
    if u.is_authenticated:
        if u.type == "DOCTOR":
            if (request.method == "POST"):
                form = CancelAppointmentRangeForm(request.POST)
                if form.is_valid():

                    # Uses same method as creation

                    # Might want to reimplement using __lte, __gte query filters instead then just deleting objects in that resulting QS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                    startdate = fromisoform(request.POST['c_startdate'])
                    startdate = date(startdate[0], startdate[1], startdate[2])
                    starttime = int(request.POST['c_starttime'])
                    enddate = fromisoform(request.POST['c_enddate'])
                    enddate = date(enddate[0], enddate[1], enddate[2])
                    endtime = int(request.POST['c_endtime'])
                    d = startdate
                    
                    all_appts = Appointment.objects.filter(doctor=u, datetime__gte=getDateTime(startdate, starttime), datetime__lte=getDateTime(enddate, endtime), time__gte=starttime, time__lte=endtime)
                    avail = all_appts.filter(booked=False)
                    booked = all_appts.filter(booked=True)
                    avail.delete()
                    if booked.exists():
                        reason = form.cleaned_data['reason']
                        try:
                            loop = asyncio.get_running_loop()
                        except RuntimeError:  # if cleanup: 'RuntimeError: There is no current event loop..'
                            loop = None

                        if loop and loop.is_running():
                            print('Async event loop already running')
                            print(booked, reason)
                            tsk = loop.create_task(send_cancellations(booked, reason))
                            # ^-- https://docs.python.org/3/library/asyncio-task.html#task-object
                            tsk.add_done_callback(                                          # optional
                                lambda t: (print(f'Task done'), booked.delete()))
                        else:
                            print('Starting new event loop')
                            asyncio.run(send_cancellations(booked, reason))
                            booked.delete()
                        
                        
                        
                    #while(d <= enddate):
                        # timeKeys are converted to strings in getKeys(), no longer
                        # timeKeys = IntTimes.getKeys()
                        # for i in range(timeKeys.index(starttime), timeKeys.index(endtime) + 1):
                        #     t = timeKeys[i]
                        #     appts = Appointment.objects.filter(doctor = u, date = str(d), time = t, booked=False)
                        #     if (appts.exists()):
                        #         appts.first().delete()
                        # d += timedelta(days=1)
                    return redirect('apptcanceled')
                else:
                    return render(request, 'doctordashboard.html', {'message': 'Oops! An error occurred.', 'doctor': Doctor.objects.get(pk=u.pk), 'cancel_mult_form': CancelAppointmentRangeForm(), 'single_appt_form': CreateAppointmentForm(initial={'doctor':u.pk}), 'mult_appt_form': CreateAppointmentRangeForm() })
    return render(request, 'doctordashboard.html')

# View for handling AJAX request during Doctor time slot scheduling, will make sure end date selection only includes times after selected start date.
# See docdash.js line 34
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
                    # smsmessage = swclient.messages.create(
                    #     body='Hi, ' + target.first_name + '. Your appointment with ' + other + ' on ' + a.dateTime + ' has been cancelled due to: ' + r + ('.\nPlease rebook an appointment for another time.' if target.type == 'PATIENT' else ''),
                    #     from_=SIGNALWIRE_NUMBER,
                    #     to='+1' + target.phone,
                    # )
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
@login_required
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
@login_required
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
@login_required
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
                        send_reminder(a.id, 'confirm')

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
@login_required
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
@login_required
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