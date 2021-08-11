# This module contains views for:
# - Opening detailed Appointment view (line 27)
#    - Uploading, deleting and downloading Appointment-related files (line 64, 84, 119)
# - Redirecting to appointment meeting url (line 144)
# - All Appointments view (line 157)

from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from health.settings import MS_TEAMS_MEETING_URL_1, MS_TEAMS_MEETING_URL_2, MS_TEAMS_MEETING_ID_LENGTH
from django.conf import settings

from .models import ApptDetails, ApptFile
from .forms import ApptDetailsForm

from book.models import Appointment

from azure.common import AzureMissingResourceHttpError

import environ

env = environ.Env()

# Create your views here.
@login_required
def details(request, pk, status=''):
    u = request.user
    if u.is_authenticated:
        # Query the appointment
        appt = Appointment.objects.filter(pk = pk)
        if appt.exists():
            appt = appt.first()

            # Make sure whoever is accessing the details is either the Patient or the Doctor
            if u == appt.patient or u == appt.doctor:
                context = {}
                message = ''
                if status == 'Success':
                    message = 'Changes made successfully.'
                elif status == 'MissingObject':
                    message = f'Your changes were made with Status Code: {status}'
                
                if message:
                    context['message'] = message
                # Query the Appointment details
                # If the details don't exist, just create the object
                p = ApptDetails.objects.filter(appt=appt)
                if (p.exists()):
                    p = p.first()
                else:
                    p = ApptDetails.objects.create(appt=appt, date=appt.date)

                # Allow Doctors to edit the details
                if u.type == 'DOCTOR':
                    if request.method == 'POST':
                        form = ApptDetailsForm(request.POST)
                        if form.is_valid():

                            files = request.FILES.getlist('files')
                            for f in files:
                                n = f.name
                                ApptFile.objects.create(appt=appt, uploaded_file=f, friendly_name=n, file_type=n[n.index('.'):], content_type=f.content_type)

                            p.prescription = form.cleaned_data['prescription']
                            p.notes = form.cleaned_data['notes']
                            p.save()
                            return redirect(reverse('details', kwargs={'pk':pk, 'status':'Success'}))
                        return redirect(reverse('details', kwargs={'pk':pk, 'status':'fail'}))
                    else:
                        # Set initial details in the form when GETting
                        form = ApptDetailsForm(initial={
                            'prescription': p.prescription,
                            'notes': p.notes,
                        })
                        context['appt']= appt
                        context['form']= form
                        
                        return render(request, 'prescription.html', context)
                else:
                    if request.method == 'POST':
                        files = request.FILES.getlist('files')

                        for f in files:
                            n = f.name
                            ApptFile.objects.create(appt=appt, uploaded_file=f, friendly_name=n, file_type=n[n.index('.'):], content_type=f.content_type)
                        return redirect(reverse('details', kwargs={'pk':appt.pk, 'status':'Success'}))
                    else:
                        context['appt'] = appt
                        context['details'] = p
                        return render(request, 'prescription.html', context)
            else:
                # If user is not the Patient or Doctor
                return render(request, 'alert.html', { 'message': 'You do not have access to this page.' })
        else:
            # If the Appointment does not exist
            return render(request, 'prescription.html', {'message': 'No Appointment found!'})
    return render(request, 'prescription.html')

@login_required
def deletefile(request, apptpk, filepk):
    appt = Appointment.objects.filter(pk=apptpk)
    u = request.user
    context = {}
    if appt.exists():
        appt = appt.first()
        p = appt.details
        context['appt'] = appt
        context['details'] = p
        context['form'] = ApptDetailsForm(initial={'prescription': p.prescription,'notes': p.notes,}) if u.type=='DOCTOR' else None 
        queried = ApptFile.objects.filter(pk=filepk)
        if u == appt.doctor or u == appt.patient:
            if queried.exists():
                queried = queried.first()
                # if settings.DEFAULT_FILE_STORAGE == 'storages.backends.azure_storage.AzureStorage':
                #     blob_name = queried.get_blob_url
                #     blob_service = settings.BLOB_SERVICE
                # try:
                #     queried.delete()
                #     blob_service.delete_blob(container_name=settings.AZURE_CONTAINER, blob_name=blob_name)
                # except AzureMissingResourceHttpError as e:
                #     print('This blob does not exist or has already been deleted. Error: ' + str(e)[str(e).index('<Message>') + len('<Message>'):str(e).index('</Message>')])
                #     queried.delete()
                #     return redirect(reverse('details', kwargs={'pk':apptpk, 'status':'AzureMissingFile'}))
                queried.delete()
                return redirect(reverse('details', kwargs={'pk':apptpk, 'status':'Success'}))
            else:
                return redirect(reverse('details', kwargs={'pk':apptpk, 'status':'MissingObject'}))
        else:
            return redirect(reverse('details', kwargs={'pk':apptpk}))
    return redirect(reverse('details', kwargs={'pk':apptpk}))
    

@login_required
def downloadfile(request, pk):
    u = request.user
    f = ApptFile.objects.filter(pk=pk)
    if f.exists():
        f = f.first()
        appt = f.appt
        if u == appt.patient or u == appt.doctor:
            filename = f.friendly_name
            response = HttpResponse(f.uploaded_file, content_type=f'{f.content_type}')
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response
        return redirect('index')
    else:
        return render(request, 'alert.html', { 'message': 'That file does not exist!', 'valid': False })

# View that redirects user to the MS Teams meeting link
# I created this as an alternative to using the entire meeting link, which can be quite lengthy
#   This is to ensure the entire link can fit into an SMS message, instead of breaking up into
#   multiple sections, becoming inaccessible for the user. This redirect only needs to add on the
#   primary key of the Appointment to the URL path.

# Example:
#   Default MS Teams Link, very long :(     : https://teams.microsoft.com/l/meetup-join/19%3ameeting_JVICXJO98BVC7Y12JF0B9IOQSACVJ98CQ1UIV7UIJ23KX2HS%40thread.v2/0?context=%7b%22Tid%22%3a%229f7e3je3-1849-3549-v55g-515f6v2s74gw%22%2c%22Oid%22%3a%220817bnr6-8y54-31t1-52x7-8h5d1c2w3a6f%22%7d
#   Redirect Link, nice, short :)           : https://health-tech.azurewebsites.net/appt/meetrdir/2
@login_required
def meeting_redir(request, pk):
    u = request.user
    appt = Appointment.objects.filter(pk=pk)
    if u.is_authenticated:
        if appt.exists():
            appt = appt.first()
            if appt.meeting_id:
                # Verify URL details and if user should have access to the Appointment
                if len(appt.meeting_id) == MS_TEAMS_MEETING_ID_LENGTH and u == appt.patient or u == appt.doctor:
                    url = MS_TEAMS_MEETING_URL_1 + appt.meeting_id + MS_TEAMS_MEETING_URL_2
                    return redirect(url)
    return redirect('index')

@login_required
def allappts(request):
    return render(request, 'allappts.html')