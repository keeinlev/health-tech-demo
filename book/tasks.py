from .models import Appointment
import time
import datetime
from django.core.mail import send_mail
import math
from health.settings import TWILIO_CLIENT as client, TWILIO_PHONE_NUMBER as twilio_phone

def send_reminder(appt_id, purpose):
    if purpose not in ['confirm', 'remind']:
        print("Error, purpose must be either \'confirm\' or \'remind\'.")
    else:
        kwords = []
        appt = Appointment.objects.filter(id=appt_id)
        if appt.exists():
            appt = appt.first()
            patient_name = appt.patient.first_name + ' ' + appt.patient.last_name
            patient_email = appt.patient.email
            patient_phone = appt.patient.phone
            doctor_name = appt.doctor.first_name + ' ' + appt.doctor.last_name
            doctor_email = appt.doctor.email
            doctor_phone = appt.doctor.phone

            if (purpose == 'confirm'):
                kwords = ['Confirmation', 'confirming']
            else:
                kwords = ['Reminder', 'a reminder for']
            
            messageVar1 = f'Use the following link to join:\n{appt.meeting_link}'
            messageVar2 = f'Use the following link to join:\n{appt.meeting_link}'

            if not appt.type:
                messageVar1 = f'The doctor will call you at the phone number you have provided: +1{appt.patient.phone}'
                messageVar2 = f'Please call the Patient at +1{appt.patient.phone}'

            # message1 = client.messages.create(
            #     body=f'Hello, {patient_name} this is {kwords[1]} your appointment with Dr. {doctor_name} on {appt.dateTime}\n\n{messageVar1}',
            #     from_=twilio_phone,
            #     to='+1' + patient_phone,
            # )
            # message2 = client.messages.create(
            #     body=f'Hello, Dr. {doctor_name} this is {kwords[1]} your appointment with Patient {patient_name} on {appt.dateTime}\n\n{messageVar2}',
            #     from_=twilio_phone,
            #     to='+1' + doctor_phone,
            # )
            if not appt.ms_event_created:
                send_mail(
                    f'{kwords[0]} for Appointment with Dr. {doctor_name}',
                    f'Hello, {patient_name} this is {kwords[1]} your appointment with Dr. {doctor_name} on {appt.dateTime}\n\n{messageVar1}',
                    'healthapptdemo@gmail.com',
                    [patient_email],
                )
                send_mail(
                    f'{kwords[0]} for Appointment with {patient_name}',
                    f'Hello, Dr. {doctor_name} this is {kwords[1]} your appointment with Patient {patient_name} on {appt.dateTime}\n\n{messageVar2}',
                    'healthapptdemo@gmail.com',
                    [doctor_email],
                )