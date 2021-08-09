# This module contains views for:
# - Booking an Appointment (lines 150, 216)
# - Cancelling an Appointment (lines 45, 107)
# - Updating page info from AJAX requests (lines 125, 229, 257)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.urls import reverse
from django.db import IntegrityError

from health.settings import MS_TEAMS_MEETING_URL_1 as meeting_url_1, MS_TEAMS_MEETING_URL_2 as meeting_url_2, MS_TEAMS_MEETING_ID_LENGTH as meeting_id_length, SMS_CARRIER, SIGNALWIRE_NUMBER, SIGNALWIRE_CLIENT as swclient

from .forms import EditAppointmentForm, CancelConfirmForm
from .models import Appointment
from .times import IntTimes
from .tasks import send_reminder, emailWrapper

from accounts.models import User, Doctor, DoctorInfo, Patient, PatientInfo

from doctordashboard.forms import CreateAppointmentForm, CreateAppointmentRangeForm, CancelAppointmentRangeForm

from pytz import timezone, utc

from random import choice
from string import ascii_letters, digits, punctuation
from datetime import date, datetime, timedelta

from graph.graph_helper import create_event
from graph.auth_helper import get_token

eastern = timezone('America/New_York')

allChars = ascii_letters + digits + digits

# Returns a random character to serve as a meeting_id
def generateMeetingId():
    return ''.join(choice(allChars) for i in range(meeting_id_length))

# Create your views here.

# View for cancelling a single Appointment, booked or unbooked
@login_required
def cancelappt(request, pk):
    u = request.user
    if u.is_authenticated:
        a = Appointment.objects.filter(pk=pk)
        if a.exists():
            a = a.first()
            if not a.apptHasPassed:
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
                        if target.sms_notifications and target.phone:
                            # send_mail(
                            #     ''
                            #     'Hi, ' + target.first_name + '. Your appointment with ' + other + ' on ' + a.shortDateTime + ' has been cancelled due to: ' + r + ('.\nPlease rebook for another time.' if target.type == 'PATIENT' else ''),
                            #     'healthapptdemo@gmail.com',
                            #     [target.phone + SMS_CARRIER],
                            # )
                            smsmessage = swclient.messages.create(
                                body='Hi, ' + target.firstOrPreferredName + '. Your appointment with ' + other + ' on ' + a.shortDateTime + ' has been cancelled due to: ' + r + ('.\nPlease rebook an appointment for another time.' if target.type == 'PATIENT' else ''),
                                from_=SIGNALWIRE_NUMBER,
                                to='+1' + target.phone,
                            )
                        send_mail(
                            'Your Appointment has been Cancelled',
                            'Hi, ' + target.first_name + '\n\nWe regret to inform you that your appointment with ' + other + ' on ' + a.dateTime + ' has been cancelled for reason:\n' + r + ('\nPlease rebook an appointment for another time.\n' if target.type == 'PATIENT' else '') + '\nWe are sorry for the inconvenience.',
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
                return render(request, 'alert.html', {'message': 'Appointment has already passed!'})
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
            return render(request, 'patientdashboard.html', {'message': 'Appointment Cancelled'})
    
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

@login_required
def doctorfilter(request):
    if request.user.is_authenticated:
        search = request.GET.get('search')
        filteredDoctors = Doctor.objects.filter(first_name__icontains=search) | Doctor.objects.filter(last_name__icontains=search) | Doctor.objects.filter(preferred_name__icontains=search)
        filteredInfos = DoctorInfo.objects.filter(certification__icontains=search) | DoctorInfo.objects.filter(consultations__icontains=search) | DoctorInfo.objects.filter(languages__icontains=search)
        for info in filteredInfos:
            filteredDoctors = filteredDoctors | Doctor.objects.filter(pk=info.user.pk)
        data = []
        for doctor in filteredDoctors:
            data.append({
                'pk': doctor.pk,
                'first_name': doctor.first_name,
                'preferred_name': doctor.preferred_name,
                'last_name': doctor.last_name,
                'qualifications': doctor.more.certification,
                'consultations': doctor.more.consultations,
                'languages': doctor.more.languages,
            })
        print(data)
        return JsonResponse({
            'doctordata':data,
            'selected': request.GET.get('selected'),
        })
    return JsonResponse({})