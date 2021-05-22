from .models import Appointment
import time
import datetime
from django.core.mail import send_mail
import math

def send_reminder(appt_id, purpose):
    if purpose not in ['confirm', 'remind']:
        print("Error, purpose must be either \'confirm\' or \'remind\'.")
    else:
        kwords = []
        appt = Appointment.objects.filter(id=appt_id).first()

        patient_name = appt.patient.first_name + ' ' + appt.patient.last_name
        patient_email = appt.patient.email
        doctor_name = appt.doctor.first_name + ' ' + appt.doctor.last_name
        doctor_email = appt.doctor.email

        if (purpose == 'confirm'):
            kwords = ['Confirmation', 'confirming']
        else:
            kwords = ['Reminder', 'a reminder for']
        
        send_mail(
            f'{kwords[0]} for Appointment with Dr. {doctor_name}',
            f'Hello, {patient_name} this is {kwords[1]} your appointment with Dr. {doctor_name} on {appt.dateTime()}\n\nUse the following link to join:\n{appt.doctor.more.meeting_url}',
            'healthapptdemo@gmail.com',
            [patient_email],
        )
        send_mail(
            f'{kwords[0]} for Appointment with {patient_name}',
            f'Hello, Dr. {doctor_name} this is {kwords[1]} your appointment with Patient {patient_name} on {appt.dateTime()}\n\nUse the following link to join:\n{appt.doctor.more.meeting_url}',
            'healthapptdemo@gmail.com',
            [doctor_email],
        )