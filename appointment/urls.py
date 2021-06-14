from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('details/<int:pk>', views.details, name='details'),
    path('meetrdir/<int:pk>', views.meeting_redir, name='meeting_redir')
]