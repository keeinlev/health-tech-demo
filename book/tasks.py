from .models import Appointment
import time
import datetime
from django.core.mail import send_mail
import math
from health.settings import SIGNALWIRE_NUMBER, SIGNALWIRE_CLIENT as swclient, CURRENT_DOMAIN
from django.urls import reverse
import asyncio
from asgiref.sync import sync_to_async

# def get_or_create_eventloop():
#     try:
#         return asyncio.get_event_loop()
#     except RuntimeError as ex:
#         if "There is no current event loop in thread" in str(ex):
#             loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(loop)
#             return asyncio.get_event_loop()

def emailWrapper(subject, body, to=[]):
    send_mail(
        subject,
        body,
        'healthapptdemo@gmail.com',
        to,
    )

# Function for sending Email and SMS confirmations/reminders for an Appointment.
# purpose signals which words to use in the message
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

            # Assignment of keywords depending on given purpose
            if (purpose == 'confirm'):
                kwords = ['Confirmation', 'confirming']
            else:
                kwords = ['Reminder', 'a reminder for']
            
            if purpose == 'confirm' or appt.reminder_sent2 < 2: #or not appt.reminder_sent:

                messageVar1 = f'\nJoin: {appt.meeting_redirect_link}'
                messageVar2 = f'\nJoin: {appt.meeting_redirect_link}'

                # Appointment type is video if True, phone if False
                if not appt.type and appt.patient.phone != None:
                    messageVar1 = f'\nThe doctor will call this number: +1{patient_phone}'
                    messageVar2 = f'\nPlease call the Patient at +1{patient_phone}'
                
                # Sending of messages
                if patient.sms_notifications and appt.patient.phone != None:
                    message1 = swclient.messages.create(
                        body=f'Hello {patient.firstOrPreferredName}\nthis is {kwords[1]} an Appointment with Dr. {doctor} {appt.shortDateTime}\n\n{messageVar1}',
                        from_=SIGNALWIRE_NUMBER,
                        to='+1' + patient_phone,
                    )
                    # SMSWrapper(
                    #     f'Appointment {kwords[0]}',
                    #     messageVar1,
                    #     patient_phone
                    # )
                if doctor.sms_notifications and appt.doctor.phone != None:
                    message2 = swclient.messages.create(
                        body=f'Hello {doctor.firstOrPreferredName}\nThis is {kwords[1]} an Appointment with {patient} {appt.shortDateTime}\n\n{messageVar2}',
                        from_=SIGNALWIRE_NUMBER,
                        to='+1' + doctor_phone,
                    )
                    # SMSWrapper(
                    #     f'Appointment {kwords[0]}',
                    #     messageVar2,
                    #     doctor_phone
                    # )
                
                # If the Appointment was created while the User was connected to MS account, reminders and confirmations will be sent by Email automatically,
                #   so no need to send them from here
                if not appt.ms_event_created:
                    # Reassignment of messageVars for Email
                    messageVar1 = f'Use the following link to join:\n{appt.meeting_redirect_link}'
                    messageVar2 = f'Use the following link to join:\n{appt.meeting_redirect_link}'

                    if not appt.type:
                        messageVar1 = f'The doctor will call you at the phone number you have provided: +1{patient_phone}'
                        messageVar2 = f'Please call the Patient at +1{patient_phone}'

                    # Sending of Emails
                    if patient.email_notifications:
                        emailWrapper(
                            f'{kwords[0]} for Appointment with Dr. {doctor}',
                            f'Hello, {patient.firstOrPreferredName}. \n\nThis is {kwords[1]} your appointment with Dr. {doctor} on {appt.dateTime}\n\n{messageVar1}',
                            [patient_email],
                        )
                    if doctor.email_notifications:
                        emailWrapper(
                            f'{kwords[0]} for Appointment with {patient}',
                            f'Hello, Dr. {doctor.fullName}. \n\nThis is {kwords[1]} your appointment with Patient {patient} on {appt.dateTime}\n\n{messageVar2}',
                            [doctor_email],
                        )
                