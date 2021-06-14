from django.shortcuts import render, redirect
from book.models import Appointment
from .models import Prescription
from .forms import PrescriptionForm
from health.settings import MS_TEAMS_MEETING_URL_1, MS_TEAMS_MEETING_URL_2

# Create your views here.
def details(request, pk):
    u = request.user
    if u.is_authenticated:
        appt = Appointment.objects.filter(pk = pk)
        if appt.exists():
            appt = appt.first()
            if u == appt.patient or u == appt.doctor:
                p = Prescription.objects.filter(appt=appt)
                if (p.exists()):
                    p = p.first()
                else:
                    p = Prescription.objects.create(appt=appt, date=appt.date)
                if u.type == 'DOCTOR':
                    if request.method == 'POST':
                        form = PrescriptionForm(request.POST)
                        if form.is_valid():
                            p.prescription = form.cleaned_data['prescription']
                            p.notes = form.cleaned_data['notes']
                            p.track_number = form.cleaned_data['track_number']
                            p.save()
                            return redirect('doctordashboard')
                    else:
                        form = PrescriptionForm(initial={
                            'prescription': p.prescription,
                            'notes': p.notes,
                            'track_number': p.track_number,
                        })
                        return render(request, 'prescription.html', {'appt': appt, 'form': form})
                else:
                    return render(request, 'prescription.html', {'appt': appt, 'details': p})
            else:
                return render(request, 'prescription.html', {'message': 'You do not have access to this page.'})
        else:
            return render(request, 'prescription.html', {'message': 'No Appointment found!'})
    return render(request, 'prescription.html')

def meeting_redir(request, pk):
    u = request.user
    appt = Appointment.objects.filter(pk=pk)
    if appt.exists():
        appt = appt.first()
        if len(appt.meeting_id) == 48 and u == appt.patient or u == appt.doctor:
            url = MS_TEAMS_MEETING_URL_1 + appt.meeting_id + MS_TEAMS_MEETING_URL_2
            return redirect(url)
    return redirect('index')