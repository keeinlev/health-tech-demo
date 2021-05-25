from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.book, name="book"),
    path('booksuccess', views.booksuccess, name='booksuccess'),
    path("doctordashboard", views.doctordashboard, name='doctordashboard'),
    path("doctordashboard/apptcreated", views.apptcreated, name='apptcreated'),
    path("doctordashboard/booksingle", views.booksingle, name='booksingle'),
    path("doctordashboard/bookmult", views.bookmult, name='bookmult'),
    url(r'^ajax/updateenddate/$', views.updateenddate, name='updateenddate'),
    url(r'^ajax/update_calendar/$', views.update_calendar, name='update_calendar'),
    url(r'^ajax/getdates/$', views.getdates, name='getdates'),
    url(r'^ajax/checkifbooked/$', views.checkifbooked, name='checkifbooked'),
    url(r'^ajax/findtimes/$', views.findtimes, name='findtimes'),
    path('cancelappointment/<int:pk>', views.cancelappt, name='cancelappt'),
    path('cancelmult', views.cancelmult, name='cancelmult'),
    path('cancelappointment/success', views.apptcanceled, name='apptcanceled')
]
