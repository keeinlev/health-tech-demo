from django.shortcuts import render

# Create your views here.
def patientdashboard(request):
    return render(request, 'patientdashboard.html', )