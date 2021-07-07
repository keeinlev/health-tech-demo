from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from health.settings import MS_TEAMS_MEETING_URL_1, MS_TEAMS_MEETING_URL_2, MS_TEAMS_MEETING_ID_LENGTH

from .models import ApptDetails
from .forms import ApptDetailsForm

from book.models import Appointment

# Create your views here.
@login_required
def details(request, pk):
    u = request.user
    if u.is_authenticated:

        # Query the appointment
        appt = Appointment.objects.filter(pk = pk)
        if appt.exists():
            appt = appt.first()

            # Make sure whoever is accessing the details is either the Patient or the Doctor
            if u == appt.patient or u == appt.doctor:

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
                            p.prescription = form.cleaned_data['prescription']
                            p.notes = form.cleaned_data['notes']
                            p.track_number = form.cleaned_data['track_number']
                            p.save()
                            return redirect('doctordashboard')
                    else:
                        # Set initial details in the form when GETting
                        form = ApptDetailsForm(initial={
                            'prescription': p.prescription,
                            'notes': p.notes,
                            'track_number': p.track_number,
                        })
                        return render(request, 'prescription.html', {'appt': appt, 'form': form})
                else:
                    # Patients can only view the details
                    return render(request, 'prescription.html', {'appt': appt, 'details': p})
            else:
                # If user is not the Patient or Doctor
                return render(request, 'prescription.html', {'message': 'You do not have access to this page.'})
        else:
            # If the Appointment does not exist
            return render(request, 'prescription.html', {'message': 'No Appointment found!'})
    return render(request, 'prescription.html')

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
            # Verify URL details and if user should have access to the Appointment
            if len(appt.meeting_id) == MS_TEAMS_MEETING_ID_LENGTH and u == appt.patient or u == appt.doctor:
                url = MS_TEAMS_MEETING_URL_1 + appt.meeting_id + MS_TEAMS_MEETING_URL_2
                return redirect(url)
    else:
        request.session['meeting_request'] = pk
        return redirect('login')
    return redirect('index')