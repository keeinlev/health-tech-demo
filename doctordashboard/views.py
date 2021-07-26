from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.urls import reverse
from django.db import IntegrityError

from health.settings import MS_TEAMS_MEETING_URL_1 as meeting_url_1, MS_TEAMS_MEETING_URL_2 as meeting_url_2, MS_TEAMS_MEETING_ID_LENGTH as meeting_id_length, SMS_CARRIER, SIGNALWIRE_NUMBER, SIGNALWIRE_CLIENT as swclient

from book.models import Appointment
from book.times import IntTimes
from book.tasks import send_reminder, emailWrapper

from .forms import CreateAppointmentForm, CreateAppointmentRangeForm, CancelAppointmentRangeForm, ApptHistoryDownloadForm

from accounts.models import User, Doctor, DoctorInfo, Patient, PatientInfo

from appointment.models import ApptDetails

from pytz import timezone, utc

from random import choice
from string import ascii_letters, digits, punctuation
from datetime import date, datetime, timedelta

from graph.graph_helper import create_event
from graph.auth_helper import get_token

import xlwt
import csv

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
    tasks = []
    for appt in appts:
        if appt.patient.sms_notifications and appt.patient.phone:
            tasks.append(async_send_mail(
                '',
                'Hi, ' + target.first_name + '. Your appointment with ' + other + ' on ' + a.shortDateTime + ' has been cancelled due to: ' + r + '.\nPlease rebook for another time.',
                appt.patient.phone + SMS_CARRIER)
            )
        if appt.patient.email_notifications:
            tasks.append(async_send_mail(
                'Your Appointment has been Cancelled',
                'Hi, ' + appt.patient.first_name + '\n\nWe regret to inform you that your appointment with Dr. ' + str(appt.doctor) + ' on ' + appt.dateTime + ' has been cancelled for reason:\n' + reason + '\nPlease rebook an appointment for another time.\n\nWe are sorry for the inconvenience.',
                to=appt.patient.email)
            )
    #print(tasks)
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
    # print(timezoneDifference)
    non_loc = datetime(date.year, date.month, date.day, time // 100, time % 100).astimezone(eastern) + timezoneDifference
    return non_loc

def getDateTimeNow():
    return getDateTime(datetime.now().date(), datetime.now().hour * 100 + datetime.now().minute)

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
def apptHistory(request):
    u=request.user

    if u.is_authenticated:
        if u.type == 'DOCTOR':
            form = ApptHistoryDownloadForm()
            if request.method == 'POST':
                form = ApptHistoryDownloadForm(request.POST)
                if form.is_valid():
                    appts = Appointment.objects.filter(doctor=u, booked=True, datetime__lt=getDateTimeNow())
                    startdate = form.cleaned_data['startdate']
                    if startdate:
                        appts = appts.filter(datetime_gte=getDateTime(startdate, 0))
                    enddate = form.cleaned_data['enddate']
                    starttime = None
                    endtime = None
                    if not form.cleaned_data['entire_day']:
                        starttime = form.cleaned_data['starttime']
                        endtime = form.cleaned_data['endtime']
                        appts = appts.filter(time__gte=starttime, time__lte=endtime)
                    patientSearch = form.cleaned_data['patient_search']
                    if patientSearch:
                        appts = appts.filter(patient__first_name__contains=patientSearch) | appts.filter(patient__preferred_name__contains=patientSearch) | appts.filter(patient__last_name__contains=patientSearch)
                    fileType = form.cleaned_data['fileformat']

                    column_keys = form.cleaned_data['fields']

                    column_choices = ApptHistoryDownloadForm().FIELDS_OPTIONS

                    columns = filter(lambda x: x[0] in column_keys, column_choices)

                    columns = list(map(lambda x: x[1], columns))

                    #columns = ['Date', 'Time', 'Consultation', 'Patient Name', 'Patient DOB', 'Patient Address', 'Patient Email', 'Patient Phone #', 'Patient OHIP', 'Patient OHIP Expiry', 'Patient Pharmacy', 'Doctor Notes', 'Prescription']

                    fileName = str(datetime.now().date()) + ' Appointment History'
                    
                    response = None
                    writer = None
                    wb = None
                    ws = None
                    font_style = None
                    if fileType == 'csv':
                        response = HttpResponse(
                            content_type='text/csv',
                            headers={'Content-Disposition': f'attachment; filename={fileName}.csv'},
                        )
                        writer = csv.writer(response)
                        writer.writerow(columns)
                    elif fileType == 'xls':
                        row_num = 0
                        # content-type of response
                        response = HttpResponse(content_type='application/ms-excel')

                        #decide file name
                        response['Content-Disposition'] = f'attachment; filename={fileName}.xls'
                        
                        #creating workbook
                        wb = xlwt.Workbook(encoding='utf-8')

                        #adding sheet
                        ws = wb.add_sheet("sheet1")

                        font_style = xlwt.XFStyle()
                        # headers are bold
                        font_style.font.bold = True

                        #write column headers in sheet
                        for col_num in range(len(columns)):
                            ws.write(row_num, col_num, columns[col_num], font_style)

                        # Sheet body, remaining rows
                        font_style = xlwt.XFStyle()
                    
                    for appt in appts:

                        col_lookup = {'Date':str(appt.date), 'Time':dict(IntTimes.choices)[appt.time], 'Consultation':appt.consultation, 'Patient Name':str(appt.patient), 'Patient DOB':str(appt.patient.more.dob), 'Patient Address':f'{appt.patient.more.address}, {appt.patient.more.postal_code}', 'Patient Email':appt.patient.email, 'Patient Phone #':str(appt.patient.phone), 'Patient OHIP':appt.patient.more.ohip_number, 'Patient OHIP Expiry':str(appt.patient.more.ohip_expiry), 'Patient Pharmacy':appt.patient.more.pharmacy, 'Doctor Notes':ApptDetails.objects.get(appt=appt).notes, 'Prescription':ApptDetails.objects.get(appt=appt).prescription}

                        if fileType == 'csv':
                            row = list(map(lambda x: col_lookup[x], columns))
                            writer.writerow(row)
                        elif fileType == 'xls':
                            row_num += 1
                            for i in range(len(columns)):
                                ws.write(row_num, i, col_lookup[columns[i]], font_style)
                    if fileType == 'xls':
                        wb.save(response)
                    return response
            else:
                return render(request, 'downloadhistory.html', {'form': form})
        return render(request, 'downloadhistory.html', {'form': form})
    return render(request, 'downloadhistory.html')


# @login_required
# def downloadApptHistory(request):
#     u=request.user
#     if u.is_authenticated:
#         if u.type == 'DOCTOR':# and (fileType == 'xls' or fileType == 'csv'):
#             if request.method == 'POST':
#                 appts = Appointment.objects.filter(doctor=u, booked=True, datetime__lt=getDateTimeNow())
                
#                 fileType=''

#                 fileName = str(datetime.now().date()) + ' Appointment History'

#                 #column header names, you can use your own headers here
#                 columns = ['Date', 'Time', 'Consultation', 'Patient Name', 'Patient DOB', 'Patient Address', 'Patient Email', 'Patient Phone #', 'Patient OHIP', 'Patient OHIP Expiry', 'Patient Pharmacy', 'Doctor Notes', 'Prescription']
                
#                 if fileType == 'xls':
#                     # content-type of response
#                     response = HttpResponse(content_type='application/ms-excel')

#                     #decide file name
#                     response['Content-Disposition'] = f'attachment; filename={fileName}.xls'

#                     #creating workbook
#                     wb = xlwt.Workbook(encoding='utf-8')

#                     #adding sheet
#                     ws = wb.add_sheet("sheet1")

#                     # Sheet header, first row
#                     row_num = 0

#                     font_style = xlwt.XFStyle()
#                     # headers are bold
#                     font_style.font.bold = True

#                     #write column headers in sheet
#                     for col_num in range(len(columns)):
#                         ws.write(row_num, col_num, columns[col_num], font_style)

#                     # Sheet body, remaining rows
#                     font_style = xlwt.XFStyle()

#                     #get your data, from database or from a text file...
#                     for appt in appts:
#                         row_num += 1
#                         print(appt.date)
#                         ws.write(row_num, 0, str(appt.date), font_style)
#                         ws.write(row_num, 1, dict(IntTimes.choices)[appt.time], font_style)
#                         ws.write(row_num, 2, appt.consultation, font_style)
#                         ws.write(row_num, 3, str(appt.patient), font_style)
#                         ws.write(row_num, 4, str(appt.patient.dob), font_style)
#                         ws.write(row_num, 5, f'{appt.patient.more.address}, {appt.patient.more.postal_code}', font_style)
#                         ws.write(row_num, 6, appt.patient.email, font_style)
#                         ws.write(row_num, 7, appt.patient.phone, font_style)
#                         ws.write(row_num, 8, appt.patient.more.ohip_number, font_style)
#                         ws.write(row_num, 9, str(appt.patient.more.ohip_expiry), font_style)
#                         ws.write(row_num, 10, appt.patient.more.pharmacy, font_style)
#                         ws.write(row_num, 11, ApptDetails.objects.get(appt=appt).notes, font_style)
#                         ws.write(row_num, 12, ApptDetails.objects.get(appt=appt).prescription, font_style)

#                     wb.save(response)
#                     return response
#                 elif fileType == 'csv':
#                     response = HttpResponse(
#                         content_type='text/csv',
#                         headers={'Content-Disposition': f'attachment; filename={fileName}.csv'},
#                     )
#                     writer = csv.writer(response)
#                     writer.writerow(columns)
                    
#                     for appt in appts:
#                         row = [str(appt.date), dict(IntTimes.choices)[appt.time], appt.consultation, str(appt.patient), str(appt.patient.dob), f'{appt.patient.more.address}, {appt.patient.more.postal_code}', appt.patient.email, str(appt.patient.phone), appt.patient.more.ohip_number, str(appt.patient.more.ohip_expiry), appt.patient.more.pharmacy, ApptDetails.objects.get(appt=appt).notes, ApptDetails.objects.get(appt=appt).prescription]
#                         writer.writerow(row)
#                         print(row)
#                     return response

#     return redirect('doctordashboard')


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
                #print(request.POST)
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
                    startdate = form.cleaned_data['startdate']
                    starttime = form.cleaned_data['starttime']
                    enddate = form.cleaned_data['enddate']
                    endtime = form.cleaned_data['endtime']
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

                    startdate = form.cleaned_data['c_startdate']
                    starttime = int(form.cleaned_data['c_starttime'])
                    enddate = form.cleaned_data['c_enddate']
                    endtime = int(form.cleaned_data['c_endtime'])
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
                            #print(booked, reason)
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
            starttime = request.GET.get('starttime', None)
            endtime = request.GET.get('endtime', None)
            is_cancel = 0
            if (not (starttime or endtime)):
                starttime = request.GET.get('c_starttime', None)
                endtime = request.GET.get('c_endtime', None)
                is_cancel = 1
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
            if int(starttime) < int(endtime):
                data['start_is_lesser'] = 1
                data['initial_end'] = int(endtime)
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
            selected_appts = Appointment.objects.filter(doctor=u, datetime__gte=datetime.now().astimezone(utc))
            if date:
                selected_appts = u.getAppts.filter(doctor=u, date=date)
            appts = []
            for a in selected_appts:
                dt = a.datetime.astimezone(timezone('America/New_York'))
                appts.append({
                    'date': str(a.date),
                    'time': f'{dt.hour % 12 if dt.hour % 12 else 12}:{"0" if dt.minute < 10 else ""}{dt.minute}{"PM" if dt.hour > 11 else "AM"}',
                    'booked': "<b style='color:" + ("red'>Booked" if a.booked else "green'>Available") + "</b>",
                    'patient': f'{a.patient.first_name} {a.patient.last_name}' if a.patient else "None",
                    'detailsurl': reverse('details', kwargs={'pk': a.pk}),
                    'meeturl': reverse('meeting_redir', kwargs={'pk': a.pk}),
                    'cancelurl': reverse('cancelappt', kwargs={'pk': a.pk}),
                })
            data = {
                'apptdata': appts,
                'all-count': len(selected_appts),
                'open-count': len(selected_appts.filter(booked=False)),
                'booked-count': len(selected_appts.filter(booked=True)),
            }
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