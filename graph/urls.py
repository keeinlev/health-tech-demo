from django.urls import path

from . import views

urlpatterns = [
    path('signin', views.sign_in, name='graphsignin'),
    path('callback', views.callback, name='callback'),
    #path('calendar', views.home, name='calendar'),
]