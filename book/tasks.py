from .models import Appointment
import time
import datetime
from django.core.mail import send_mail
import math
#from health.settings import TWILIO_CLIENT as client, TWILIO_PHONE_NUMBER as twilio_phone, SIGNALWIRE_PROJECT, SIGNALWIRE_TOKEN, SIGNALWIRE_CLIENT as swclient
from health.settings import TWILIO_PHONE_NUMBER as twilio_phone, SIGNALWIRE_NUMBER, SIGNALWIRE_CLIENT as client, CURRENT_DOMAIN
from django.urls import reverse

def send_reminder(appt_id, purpose):
    if purpose not in ['confirm', 'remind']:
        print("Error, purpose must be either \'confirm\' or \'remind\'.")
    else:
        kwords = []
        appt = Appointment.objects.filter(id=appt_id)
        if appt.exists():
            appt = appt.first()
            patient = appt.patient
            doctor = appt.doctor
            patient_email = patient.email
            patient_phone = patient.phone
            doctor_email = doctor.email
            doctor_phone = doctor.phone

            if (purpose == 'confirm'):
                kwords = ['Confirmation', 'confirming']
            else:
                kwords = ['Reminder', 'a reminder for']
            
            redirect_url = 'https://health-tech.azurewebsites.net' + reverse('meeting_redir', kwargs={'pk':appt.pk})

            messageVar1 = f'Join: {redirect_url}'
            messageVar2 = f'Join: {redirect_url}'

            if not appt.type:
                messageVar1 = f'The doctor will call you at the phone number you have provided: +1{patient_phone}'
                messageVar2 = f'Please call the Patient at +1{patient_phone}'

            message1 = client.messages.create(
                body=f'Hello {patient.first_name}\nthis is {kwords[1]} an Appointment with Dr. {doctor} {appt.shortDateTime}\n\n{messageVar1}',
                from_=SIGNALWIRE_NUMBER,
                to='+1' + patient_phone,
            )
            
            message2 = client.messages.create(
                body=f'Hello {doctor.first_name}\nthis is {kwords[1]} an Appointment with {patient} {appt.shortDateTime}\n\n{messageVar2}',
                from_=SIGNALWIRE_NUMBER,
                to='+1' + doctor_phone,
            )
            
            messageVar1 = f'Use the following link to join:\n{appt.meeting_link}'
            messageVar2 = f'Use the following link to join:\n{appt.meeting_link}'

            if not appt.type:
                messageVar1 = f'The doctor will call you at the phone number you have provided: +1{patient_phone}'
                messageVar2 = f'Please call the Patient at +1{patient_phone}'
            #Confirmation: Appt with Patient patient_name on Mon Sep 12 2021

            if not appt.ms_event_created:
                send_mail(
                    f'{kwords[0]} for Appointment with Dr. {doctor}',
                    f'Hello, {patient} this is {kwords[1]} your appointment with Dr. {doctor} on {appt.dateTime}\n\n{messageVar1}',
                    'healthapptdemo@gmail.com',
                    [patient_email],
                )
                send_mail(
                    f'{kwords[0]} for Appointment with {patient}',
                    f'Hello, Dr. {doctor} this is {kwords[1]} your appointment with Patient {patient} on {appt.dateTime}\n\n{messageVar2}',
                    'healthapptdemo@gmail.com',
                    [doctor_email],
                )