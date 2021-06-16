from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path("register", views.register, name="register"),

    url(r'^ajax/validate_email_and_ohip/$', views.validate_email_and_ohip, name='validate_email_and_ohip'),  # called during registration to ensure the email/ohip is not taken yet, views line 153
    
    path('need_activate', views.activateprompt, name='activateprompt'), # redirects to an alert asking for confirmation, views line 184
    
    path('activate/<uidb64>/<token>', views.activate, name='activate'), # account activation after registration, views line 188
    
    path('confirmation/success', views.confirmsuccess, name='confirmsuccess'), # these two redirect to ensure the request data from activation
                                                                               # stays in the past and can't be reloaded, i.e. one time use, views line 201 and 205
    path('confirmation/failure', views.confirmfail, name='confirmfail'),
    
    path('editprofile', views.editprofile, name='editprofile'), # views line 85
    
    path("logout_redir", views.logout_redir, name="logout_redir"), # views line 174
]
