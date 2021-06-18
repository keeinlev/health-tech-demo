from .models import Appointment
import time
import datetime
from django.core.mail import send_mail
import math
from health.settings import CA_CARRIERS_LIST, DJANGO_DEVELOPMENT#SIGNALWIRE_NUMBER, SIGNALWIRE_CLIENT as client, CURRENT_DOMAIN
from django.urls import reverse
import asyncio
from asgiref.sync import sync_to_async

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

async def emailWrapper(subject, body, to=[]):
    send_mail(
        subject,
        body,
        'healthtechdemo@gmail.com',
        to,
    )
############################################################################## IT LOOKS LIKE FIDO MIGHT WORK FOR EVERY CARRIER!!!!!!!!!!!!!!
async def SMSWrapper(subject, body, to):
    send_mail(
        subject,
        body,
        'healthapptdemo@gmail.com',
        [f'{to}{c}' for c in CA_CARRIERS_LIST]
    )

# Function for sending Email and SMS confirmations/reminders for an Appointment.
# purpose signals which words to use in the message
@sync_to_async
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
            
            # Piecing together the short redirect URL using the primary key
            redirect_url = 'https://health-tech.azurewebsites.net' + reverse('meeting_redir', kwargs={'pk':appt.pk})

            messageVar1 = f'\nJoin: {redirect_url}'
            messageVar2 = f'\nJoin: {redirect_url}'

            # Appointment type is video if True, phone if False
            if not appt.type:
                messageVar1 = f'\nThe doctor will call this number: +1{patient_phone}'
                messageVar2 = f'\nPlease call the Patient at +1{patient_phone}'
            
            # Sending of messages
            loop = get_or_create_eventloop()
            #futures = []
            futures = [loop.create_task(
                SMSWrapper(
                    f'Appointment {kwords[0]}',
                    messageVar1,
                    patient_phone
                )
            )]
            futures = futures + [loop.create_task(
                SMSWrapper(
                    f'Appointment {kwords[0]}',
                    messageVar2,
                    doctor_phone
                )
            )]
            
            # message1 = client.messages.create(
            #     body=f'Hello {patient.first_name}\nthis is {kwords[1]} an Appointment with Dr. {doctor} {appt.shortDateTime}\n\n{messageVar1}',
            #     from_=SIGNALWIRE_NUMBER,
            #     to='+1' + patient_phone,
            # )
            # message2 = client.messages.create(
            #     body=f'Hello {doctor.first_name}\nthis is {kwords[1]} an Appointment with {patient} {appt.shortDateTime}\n\n{messageVar2}',
            #     from_=SIGNALWIRE_NUMBER,
            #     to='+1' + doctor_phone,
            # )

            # If the Appointment was created while the User was connected to MS account, reminders and confirmations will be sent by Email automatically,
            #   so no need to send them from here
            if not appt.ms_event_created:
                # Reassignment of messageVars for Email
                messageVar1 = f'Use the following link to join:\n{appt.meeting_link}'
                messageVar2 = f'Use the following link to join:\n{appt.meeting_link}'

                if not appt.type:
                    messageVar1 = f'The doctor will call you at the phone number you have provided: +1{patient_phone}'
                    messageVar2 = f'Please call the Patient at +1{patient_phone}'

                # Sending of Emails
                futures.append(loop.create_task(
                    emailWrapper(
                        f'{kwords[0]} for Appointment with Dr. {doctor}',
                        f'Hello, {patient} this is {kwords[1]} your appointment with Dr. {doctor} on {appt.dateTime}\n\n{messageVar1}',
                        [patient_email],
                    )
                ))
                futures.append(loop.create_task(
                    emailWrapper(
                        f'{kwords[0]} for Appointment with {patient}',
                        f'Hello, Dr. {doctor} this is {kwords[1]} your appointment with Patient {patient} on {appt.dateTime}\n\n{messageVar2}',
                        [doctor_email],
                    )
                ))

            #print(futures)
            loop.run_until_complete(asyncio.wait(futures))
            loop.close()
            #asyncio.gather(*futures)

                