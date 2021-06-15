from django.shortcuts import render, redirect
from .forms import CreateAppointmentForm, CreateAppointmentRangeForm, CancelAppointmentRangeForm, EditAppointmentForm, CancelConfirmForm
from accounts.models import User, Doctor, DoctorInfo, Patient, PatientInfo
from .models import Appointment
from appointment.models import Prescription
from django.http import HttpResponse, JsonResponse
from .times import IntTimes
from datetime import date, datetime, timedelta
from .tasks import send_reminder
from django.core.mail import send_mail
from django.urls import reverse
from pytz import timezone, utc
from health.settings import MS_TEAMS_MEETING_URL_1 as meeting_url_1, MS_TEAMS_MEETING_URL_2 as meeting_url_2#, SIGNALWIRE_NUMBER, SIGNALWIRE_CLIENT as swclient
from random import choice
from string import ascii_letters, digits, punctuation
from django.db import IntegrityError
from graph.graph_helper import create_event
from graph.auth_helper import get_token

eastern = timezone('America/New_York')
allChars = ascii_letters + digits + digits

def generateMeetingId():
    return ''.join(choice(allChars) for i in range(48))

def fromisoform(d):
    year = int(d[:4])
    month = int(d[5:7])
    day = int(d[8:10])
    return (year, month, day)

def getCurrentTimeKey():
    hour = datetime.now().hour
    minute = datetime.now().minute
    return hour * 100 + minute

def getDateTime(date, time):
    non_loc = datetime(date.year, date.month, date.day, time // 100, time % 100).astimezone(utc)
    return non_loc


# Create your views here.

def doctordashboard(request):
    u = request.user
    if u.is_authenticated:
        if u.type == "DOCTOR":
            single_appt_form = CreateAppointmentForm(initial={'doctor':u.pk})
            mult_appt_form = CreateAppointmentRangeForm()
            cancel_mult_form = CancelAppointmentRangeForm()
            if (request.method == "GET"):
                return render(request, 'doctordashboard.html', {'doctor': Doctor.objects.get(pk=u.pk), 'cancel_mult_form': cancel_mult_form, 'single_appt_form': single_appt_form, 'mult_appt_form': mult_appt_form })
    return render(request, 'doctordashboard.html')

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

def booksingle(request):
    u=request.user
    if u.is_authenticated:
        print('checkpoint1')
        if u.type == "DOCTOR":
            print('checkpoint2')
            if (request.method == "POST"):
                print('checkpoint3')
                form = CreateAppointmentForm(request.POST)
                print(request.POST)
                if form.is_valid():
                    print('checkpoint4')
                    appt = form.save(commit=False)
                    appt.doctor = u
                    appt.datetime = getDateTime(form.cleaned_data['date'], int(form.cleaned_data['time']))
                    appt.save()
                    ps = Prescription.objects.create(date=appt.date, appt=appt)
                    return redirect('apptcreated')
                else:
                    return render(request, 'doctordashboard.html', {'doctor': Doctor.objects.get(pk=u.pk), 'cancel_mult_form': CancelAppointmentRangeForm(), 'single_appt_form': CreateAppointmentForm(initial={'doctor':u.pk}), 'mult_appt_form': CreateAppointmentRangeForm(), 'message':form.errors})
    return render(request, 'doctordashboard.html')

def bookmult(request):
    u=request.user
    if u.is_authenticated:
        if u.type == "DOCTOR":
            if (request.method == "POST"):
                form = CreateAppointmentRangeForm(request.POST)
                if form.is_valid():
                    startdate = fromisoform(request.POST['startdate'])
                    startdate = date(startdate[0], startdate[1], startdate[2])
                    starttime = request.POST['starttime']
                    enddate = fromisoform(request.POST['enddate'])
                    enddate = date(enddate[0], enddate[1], enddate[2])
                    endtime = request.POST['endtime']
                    d = startdate
                    while(d <= enddate):
                        timeKeys = IntTimes.getKeys()
                        for i in range(timeKeys.index(starttime), timeKeys.index(endtime) + 1):
                            t = timeKeys[i]
                            if not (Appointment.objects.filter(doctor = u, date = str(d), time = t).exists()):
                                a = Appointment.objects.create(doctor = u, date = str(d), time = t, datetime=getDateTime(d, int(t)))
                                Prescription.objects.create(appt=a, date=a.date)
                        d += timedelta(days=1)
                    return redirect('apptcreated')
                else:
                    return render(request, 'doctordashboard.html', {'message': 'Oops! An error occurred.', 'doctor': Doctor.objects.get(pk=u.pk), 'cancel_mult_form': CancelAppointmentRangeForm(), 'single_appt_form': CreateAppointmentForm(initial={'doctor':u.pk}), 'mult_appt_form': CreateAppointmentRangeForm() })
        else:
            pass
    return render(request, 'doctordashboard.html')

def cancelmult(request):
    u=request.user
    if u.is_authenticated:
        if u.type == "DOCTOR":
            if (request.method == "POST"):
                form = CancelAppointmentRangeForm(request.POST)
                if form.is_valid():
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

def patientsearch(request):
    u = request.user
    if (u.is_authenticated):
        if u.type == "DOCTOR":
            searched = request.GET.get('patient-search')
            date = request.GET.get('date', None)
            query = u.getAppts.filter(patient__first_name__contains=searched) | u.getAppts.filter(patient__last_name__contains=searched)
            if date != '0':
                query = u.getAppts.filter(date=date, patient__first_name__contains=searched) | u.getAppts.filter(date=date, patient__last_name__contains=searched)
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

############# Reminder: make a condition for patients cancelling
def cancelappt(request, pk):
    u = request.user
    if u.is_authenticated:
        a = Appointment.objects.filter(pk=pk)
        if a.exists():
            a = a.first()
            if request.method == "POST":
                form = CancelConfirmForm(request.POST)
                if form.is_valid():
                    target = a.doctor
                    other = f'Patient {a.patient}'
                    if u.type == "DOCTOR":
                        target = a.patient
                        other = f'Dr. {a.doctor}'
                    r = form.cleaned_data['reason']
                    # smsmessage = swclient.messages.create(
                    #     body='Hi, ' + target.first_name + '. Your appointment with ' + other + ' on ' + a.dateTime() + ' has been cancelled due to: ' + r + ('.\nPlease rebook an appointment for another time.' if target.type == 'PATIENT' else ''),
                    #     from_=SIGNALWIRE_NUMBER,
                    #     to='+1' + target.phone,
                    # )
                    send_mail(
                        'Your Appointment has been Cancelled',
                        'Hi,' + target.first_name + '\n\nWe are sorry to inform you that your appointment with ' + other + ' on ' + a.dateTime() + ' has been cancelled for reason:\n' + r + ('\nPlease rebook an appointment for another time.\n' if target.type == 'PATIENT' else '') + '\nWe are sorry for the inconvenience.',
                        'healthapptdemo@gmail.com',
                        [target.email],
                    )
                    a.delete()
                    return redirect('apptcanceled')
            else:
                if a.booked:
                    form = CancelConfirmForm(initial={
                        'doctor': a.doctor,
                        'patient': a.patient,
                        'date': a.date,
                        'time': a.time,
                    })
                    return render(request, 'confirmcancel.html', { 'appt': a , 'form': form, 'dt': a.dateTime() })
                else:
                    a.delete()
                    return redirect('apptcanceled')
        else:
            return render(request, 'alert.html', {'message': 'Appointment does not exist!'})
    return render(request, 'doctordashboard.html')


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
                        while(1):
                            try:
                                a.meeting_id = meeting_id
                                a.save()
                                break
                            except IntegrityError as e:
                                print(e + ', trying new meeting_id')
                                meeting_id = generateMeetingId()

                        send_reminder(a.id, 'confirm')

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

                        return redirect('booksuccess')
                    else:
                        error = 'The Appointment you tried to book either does not exist or has already been booked.'
                        return render(request, 'book.html', { 'error_message': error, 'doctors': Doctor.objects.all(), 'doctorsinfo': DoctorInfo.objects.all(), 'form': form })
                else:
                    return render(request, 'book.html', {'form': form, 'doctors': Doctor.objects.all(), 'doctorsinfo': DoctorInfo.objects.all()})
            else:
                return render(request, 'book.html', {'form': form, 'doctors': Doctor.objects.all(), 'doctorsinfo': DoctorInfo.objects.all()})
    return render(request, 'book.html')

def booksuccess(request):
    u=request.user
    if u.is_authenticated:
        if u.type == "PATIENT":
            form = EditAppointmentForm()
            if (request.method == "GET"):
                message = "Appointment Booked."
                return render(request, 'book.html', {'form': form, 'doctors': Doctor.objects.all(), 'doctorsinfo': DoctorInfo.objects.all(), 'message':message})
    return render(request, 'book.html')


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