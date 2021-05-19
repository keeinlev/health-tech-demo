from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('prescription/<int:pk>', views.prescription, name='prescription')
]