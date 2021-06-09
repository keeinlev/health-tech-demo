from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path("register", views.register, name="register"),
    url(r'^ajax/validate_email/$', views.validate_email, name='validate_email'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('confirmation/success', views.confirmsuccess, name='confirmsuccess'),
    path('confirmation/failure', views.confirmfail, name='confirmfail'),
    path('need_activate', views.activateprompt, name='activateprompt'),
    path('editprofile', views.editprofile, name='editprofile'),
    #path("login", views.login, name="login"),
    path("logout_redir", views.logout_redir, name="logout_redir"),
    #path("doctorlogin", views.doctorlogin, name="doctorlogin"),
]
