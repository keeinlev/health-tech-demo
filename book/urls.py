from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.book, name="book"),
    path('booksuccess', views.booksuccess, name='booksuccess'),
    url(r'^ajax/update_calendar/$', views.update_calendar, name='update_calendar'),
    url(r'^ajax/findtimes/$', views.findtimes, name='findtimes'),
    path('cancelappointment/<int:pk>', views.cancelappt, name='cancelappt'),
    path('cancelappointment/success', views.apptcanceled, name='apptcanceled'),
]
