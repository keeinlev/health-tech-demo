from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from .forms import SignUpForm, DoctorEditForm, PatientEditForm
from .models import User, Patient, Doctor, PatientInfo, DoctorInfo
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.core.mail import send_mail

from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator

from graph.auth_helper import remove_user_and_token

from health.settings import SMS_CARRIER


# Create your views here.

# View for registration
def register(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # If the form is valid, we know there are valid entries for:
            #   First/Last name
            #   Both email fields                                       (these will be verified to match again later)
            #   Both password fields                                    (these will be verified to match again later)
            #   DOB
            #   Phone                                                   (not null, but length will be verified)
            #   OHIP number                                             (not null, but length will be verified)
            #   OHIP version and expiry                                 (not null, but length will be verified)
            # Getting all the data into shape for saving
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            preferred_name = form.cleaned_data['preferred_name']
            dob = form.cleaned_data['dob']
            email = form.cleaned_data['email1']
            password = form.cleaned_data['password1']
            phone = str(form.cleaned_data['phone'])
            ohip_number = str(form.cleaned_data['ohip'])
            ohip_version_code = form.cleaned_data['ohip_version']

            # Making sure phone and ohip number are both 'XXXXXXXXXX', number-only entry is handled on frontend in register.js
            if len(phone) != 10 or len(ohip_number) != 10 or len(ohip_version_code) != 2:
                message = "Registration unsuccessful. Please make sure phone and OHIP numbers are in the correct format."
                return render(request, "register.html", {'form': form, 'message': message})

            # OHIP formatting into 'XXXX-XXX-XXX-XX'
            ohip_number = ohip_number[:4] + '-' + ohip_number[4:7] + '-' + ohip_number[7:]
            ohip_number = ohip_number + '-' + ohip_version_code
            ohip_number = ohip_number.upper()
            ohip_expiry = form.cleaned_data['ohip_expiry']
            
            # Emails and passwords must match, this is the second layer of verification after frontend in register.js
            if (email != form.cleaned_data['email2'] or password != form.cleaned_data['password2']):
                message = "Registration unsuccessful. Please make sure emails and passwords match."
                return render(request, "register.html", {'form': form, 'message': message})

            # See if all fields can create a valid User object
            try:
                # If u is not created, will go straight to except block
                # Through the form, first_name, last_name and dob have already been verified
                # Through manual checking, phone and email have already been verified
                # If we get an error here, it's because the email was valid, but already exists
                u = User.objects.create(first_name=first_name, last_name=last_name, preferred_name=preferred_name, phone=phone, email=email, dob=dob, type=User.Types.PATIENT, is_active=False)
                
                # We verified the length/format of ohip_number already and ohip_expiry was verified by the form
                # If we get an error here, it's because the ohip number was valid, but already exists
                # However, we already created u, so we must delete it later (it should be the last user in the model Queryset)
                PatientInfo.objects.create(user=u, ohip_number=ohip_number, ohip_expiry=ohip_expiry)

            except IntegrityError as e:
                # IntegrityError catches non-unique entries for fields that must be unique
                cause = str(e.__cause__)

                # String splicing to get the cause of the error
                cleancause = cause[cause.index("UNIQUE constraint failed: ") + len("UNIQUE constraint failed: "):]
                unique_constraint = cleancause[cleancause.index('.') + 1:].capitalize().replace('_', ' ')
                
                if unique_constraint == 'Ohip number':
                    unique_constraint = 'OHIP Number'

                    # As mentioned before, we delete the last created Patient
                    Patient.objects.last().delete()
                
                # Error message returned to the template
                return render(request, "register.html", {'form': form, 'message': unique_constraint + ' already registered to existing account!'})
            
            # If nothing goes wrong, set the password.
            # set_password is Django built-in and uses PBKDF2 algorithm and SHA256 hash
            u.set_password(password)
            u.save()

            # Build the token for account confirmation
            domain = get_current_site(request).domain
            uidb64 = urlsafe_base64_encode(force_bytes(u.pk))
            link = reverse('activate', kwargs={'uidb64':uidb64, 'token':default_token_generator.make_token(u),})
            activate_url = 'http://' + domain + link

            # Send initial SMS consent Message
            send_mail(
                '',
                'You will now receive SMS notifications for your booked appointments',
                'healthapptdemo@gmail.com',
                [u.phone + SMS_CARRIER],
            )

            # Send a confirmation email
            send_mail(
                'Confirm your Online Health Account',
                'Hi,' + u.first_name + '\n\nPlease use the following link to confirm your email:\n' + activate_url,
                'healthapptdemo@gmail.com',
                [u.email],
            )
            return redirect('activateprompt')
        else:
            message = "Registration unsuccessful. Please make sure you have filled all fields in correctly."
            return render(request, "register.html", {'form': form, 'message': message})
    
    # If the request is GET, just return an empty form to the template
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})

# View for editing profiles
def editprofile(request):
    u = request.user
    if u.is_authenticated:
        form = None
        if request.method == 'POST':
            if u.type == "DOCTOR":
                # These forms are defined in forms.py
                form = DoctorEditForm(request.POST)
            else:
                form = PatientEditForm(request.POST)
            if form.is_valid():
                if u.type == 'DOCTOR':
                    # Updates the DoctorInfo object associated to u
                    di = DoctorInfo.objects.filter(user = u).first()
                    di.certification = form.cleaned_data['qualifications']
                    di.consultations = form.cleaned_data['consultations']
                    di.languages = form.cleaned_data['languages']
                    di.save()
                else:
                    try:
                        # Updates the PatientInfo object associated to u, but have to catch possible non-unique OHIP number
                        pi = PatientInfo.objects.filter(user = u).first()
                        pi.ohip_number = str(form.cleaned_data['ohip1']) + '-' + str(form.cleaned_data['ohip2']) + '-' + str(form.cleaned_data['ohip3']) + '-' + form.cleaned_data['ohip_version'].upper()
                        pi.ohip_expiry = form.cleaned_data['ohip_expiry']
                        pi.save()
                    except IntegrityError as e:
                        return render(request, "editprofile.html", {'form': form, 'message': 'OHIP number already registered to existing account!'})
                
                # These fields are shared by both Patients and Doctors, so can just save to the general user
                u.first_name = form.cleaned_data['first_name']
                u.last_name = form.cleaned_data['last_name']
                u.dob = form.cleaned_data['dob']
                u.phone = str(form.cleaned_data['phone1']) + str(form.cleaned_data['phone2']) + str(form.cleaned_data['phone3'])
                print(form.cleaned_data['sms_notis'])
                print(form.cleaned_data['email_notis'])
                u.sms_notifications = form.cleaned_data['sms_notis']
                u.email_notifications = form.cleaned_data['email_notis']
                u.save()

            return redirect('index')
        
        # Handle GET request
        else:
            if u.type == "DOCTOR":
                d = Doctor.objects.filter(id=u.id).first()

                # Put all the existing user information as initial values in the form
                form = DoctorEditForm(initial={
                    'first_name': d.first_name,
                    'last_name': d.last_name,
                    'dob': d.dob,
                    'phone1': d.phone[:3],
                    'phone2': d.phone[3:6],
                    'phone3': d.phone[6:],
                    'email_notis': d.email_notifications,
                    'sms_notis': d.sms_notifications,
                    'qualifications': d.more.certification,
                    'consultations': d.more.consultations,
                    'languages': d.more.languages,
                })
                return render(request, 'editprofile.html', {'form': form, 'doctor': d, 'consultations': d.more.consultations.split(', '), 'languages': d.more.languages.split(', '),})
            else:
                p = Patient.objects.filter(id=u.id).first()

                # Put all the existing user information as initial values in the form
                form = PatientEditForm(initial={
                    'first_name': p.first_name,
                    'last_name': p.last_name,
                    'dob': p.dob,
                    'phone1': p.phone[:3],
                    'phone2': p.phone[3:6],
                    'phone3': p.phone[6:],
                    'email_notis': p.email_notifications,
                    'sms_notis': p.sms_notifications,
                    'ohip1': p.more.ohip_number[:4],
                    'ohip2': p.more.ohip_number[5:8],
                    'ohip3': p.more.ohip_number[9:12],
                    'ohip_version': p.more.ohip_number[13:],
                    'ohip_expiry': p.more.ohip_expiry,
                })
                return render(request, 'editprofile.html', {'form': form, 'patient': p,})

    # If user is not signed in, template logic will handle appropriate page display
    return render(request, 'editprofile.html')

# View handling AJAX request for checking email and OHIP uniqueness during registration, see register.js line 46
def validate_email_and_ohip(request):
    email = request.GET.get('email1', None)
    ohip = str(request.GET.get('ohip', None))
    ohip_version = request.GET.get('ohip_version', None)
    ohip = '-'.join([ohip[:4], ohip[4:7], ohip[7:], str(ohip_version)])
    data = {
        'email_is_taken': User.objects.filter(email__iexact=email).exists(),                # Two boolean values, True if the field is taken, False if it is unique
        'ohip_is_taken': PatientInfo.objects.filter(ohip_number__iexact=ohip).exists(),
    }

    # Prepare an error message based on which field is non-unique
    if data['email_is_taken']:
        data['error_message'] = 'Email already registered to existing account!'
    if data['ohip_is_taken']:
        if 'error_message' in data:
            data['error_message'] += '<br />OHIP Number already registered to existing account!'
        else:
            data['error_message'] = "OHIP Number already registered to existing account!"

    # Returns to AJAX success function, register.js line 51
    return JsonResponse(data)

# View set for LOGOUT_REDIRECT_URL
def logout_redir(request):
    user = request.user
    if (user.is_authenticated):

        # remove_user_and_token clears the session of any existing MS login token, and sets the user's ms_authenticated field to False, see graph.auth_helper line 87
        remove_user_and_token(request)
        
        # logout is included from Django Authentication URLs under accounts (see health.urls), full URL is 'accounts/logout' but logic is built-in to Django
        return redirect('logout')
    return redirect('index')

def activateprompt(request):
    message = f'Please check your email for a confirmation message.'
    return render(request, 'alert.html', { 'message': message, 'valid': True, 'media': 'sms' })

# View for activating a new User
def activate(request, uidb64, token):
    try:
        # Query User using decoded UID
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # This will fail if the user is already activated, the token is invalid, or the UID is invalid
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('confirmsuccess')
    else:
        return redirect('confirmfail')

# Redirects after successful activation
def confirmsuccess(request):
    message = f'Thank you for confirming your email.'
    return render(request, 'alert.html', { 'message': message, 'valid': True })

# Redirects after failed activation
def confirmfail(request):
    return render(request, 'alert.html', { 'message': 'Email activation invalid.', 'valid': False })