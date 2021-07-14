from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [    
    path("", views.doctordashboard, name='doctordashboard'),
    path("apptcreated", views.apptcreated, name='apptcreated'),
    path("booksingle", views.booksingle, name='booksingle'),
    path("bookmult", views.bookmult, name='bookmult'),
    url(r'^ajax/updateenddate/$', views.updateenddate, name='updateenddate'),
    url(r'^ajax/showreasontextbox/$', views.showreasontextbox, name='showreasontextbox'),
    url(r'^ajax/getdates/$', views.getdates, name='getdates'),
    url(r'^ajax/patientsearch/$', views.patientsearch, name='patientsearch'),
    url(r'^ajax/checkifbooked/$', views.checkifbooked, name='checkifbooked'),
    path('cancelmult', views.cancelmult, name='cancelmult'),
    path('apptHistory', views.apptHistory, name='appthistory'),
]