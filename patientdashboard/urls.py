from django.urls import path
from patientdashboard import views

urlpatterns = [
    path('', views.patientdashboard, name='patientdashboard'),
]