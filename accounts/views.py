# This module contains views for:
# - Registering new Patients (line 52)
# - Registering new Doctors (line 178)
# - Confirming email on registration (lines 308, 318, 340, 345)
# - Editing profiles (line 350)
#    - Editing Patient pharmacy choice (lines 497 517 523 527)
#    - Requesting and confirming email changes (line 532)

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required

from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator

from .forms import SignUpForm, PatientSignUpForm, DoctorEditForm, PatientEditForm
from .models import User, Patient, Doctor, PatientInfo, DoctorInfo

from graph.auth_helper import remove_user_and_token
from maps.maps_helper import geocode, get_nearby, find_place_by_place_id

from health.settings import SMS_CARRIER, GOOGLE_MAPS_API_KEY

from pprint import pprint

def getProtocol(request):
    domain = get_current_site(request).domain
    if domain == 'health-tech.azurewebsites.net':
        return 'https'
    else:
        return 'http'

def cleanNumberField(s):
    new = ''
    for c in s:
        try:
            new += str(int(c))
        except ValueError as e:
            pass
    return new

# Create your views here.

# View for registration
def register(request):
    if not request.user.is_authenticated:
        form = PatientSignUpForm()
        if request.method == 'POST':
            form = PatientSignUpForm(request.POST)
            if form.is_valid():
                # If the form is valid, we know there are valid entries for:
                #   First/Last name
                #   Both email fields                                       (these will be verified to match again later)
                #   Both password fields                                    (these will be verified to match again later)
                #   DOB
                #   Phone                                                   (not null, but length will be verified)
                #   OHIP number                                             (not null, but length will be verified)
                #   OHIP expiry                                             (not null, but length will be verified)
                # Getting all the data into shape for saving
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                preferred_name = form.cleaned_data['preferred_name']
                dob = form.cleaned_data['dob']
                email = form.cleaned_data['email1']
                password = form.cleaned_data['password1']
                phone = form.cleaned_data['phone']
                if phone:
                    phone = cleanNumberField(str(phone))
                else:
                    phone = None

                # Getting Address lat/long
                address = form.cleaned_data['address']
                postal_code = form.cleaned_data['postal_code']
                geocode_res = geocode(address, postal_code)
                if (geocode_res['status'] != 'OK'):
                    message = "Registration unsuccessful. Address and/or Postal Code not found."
                    return render(request, "register.html", {'form': form, 'message': message})
                coords = geocode_res["results"][0]["geometry"]["location"]
                coords = f'{coords["lat"]},{coords["lng"]}'
                #print(geocode_res['results'][0]['formatted_address'])

                ohip_number = form.cleaned_data['ohip']

                # Making sure phone number is 'XXXXXXXXXX', number-only entry is handled on frontend in register.js
                if (phone and len(phone) != 10):
                    message = "Registration unsuccessful. Please make sure phone number is in the correct format."
                    return render(request, "register.html", {'form': form, 'message': message})

                # OHIP checking format 'XXXX-XXX-XXX-XX'
                if (len(ohip_number) != 15 or ohip_number[4] != '-' or ohip_number[8] != '-' or ohip_number[12] != '-'):
                    message = "Registration unsuccessful. Please make sure OHIP number is in the correct format."
                    return render(request, "register.html", {'form': form, 'message': message})
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
                    u = User.objects.create(first_name=first_name, last_name=last_name, preferred_name=preferred_name, phone=phone, email=email, type=User.Types.PATIENT, is_active=False)
                    if phone == None:
                        u.sms_notifications = False
                        u.save()
                    # We verified the length/format of ohip_number already and ohip_expiry was verified by the form
                    # If we get an error here, it's because the ohip number was valid, but already exists
                    # However, we already created u, so we must delete it later
                    PatientInfo.objects.create(user=u, dob=dob, address=address, postal_code=postal_code, address_coords=coords, ohip_number=ohip_number, ohip_expiry=ohip_expiry)

                except IntegrityError as e:
                    # IntegrityError catches non-unique entries for fields that must be unique
                    cause = str(e.__cause__)

                    # String splicing to get the cause of the error
                    cleancause = cause[cause.index("UNIQUE constraint failed: ") + len("UNIQUE constraint failed: "):]
                    unique_constraint = cleancause[cleancause.index('.') + 1:].capitalize().replace('_', ' ')
                    
                    if unique_constraint == 'Ohip number':
                        unique_constraint = 'OHIP Number'

                        # As mentioned before, we delete the last created Patient
                        u.delete()
                    
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
                activate_url = getProtocol(request) + '://' + domain + link

                # Send initial SMS consent Message
                # send_mail(
                #     '',
                #     'You will now receive SMS notifications for your booked appointments',
                #     'healthapptdemo@gmail.com',
                #     [u.phone + SMS_CARRIER],
                # )

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
            form = PatientSignUpForm()
        return render(request, 'register.html', {'form': form})
    return redirect('index')

def registerdoctor(request):
    if not request.user.is_authenticated:
        form = SignUpForm()
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                # Getting all the data into shape for saving
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                preferred_name = form.cleaned_data['preferred_name']
                email = form.cleaned_data['email1']
                password = form.cleaned_data['password1']
                phone = form.cleaned_data['phone']
                if phone:
                    phone = cleanNumberField(str(phone))
                else:
                    phone = None

                # Getting Address lat/long
                address = form.cleaned_data['address']
                coords = None
                if address:
                    geocode_res = geocode(address, '')
                    if (geocode_res['status'] != 'OK'):
                        message = "Registration unsuccessful. Address not found."
                        return render(request, "docregister.html", {'form': form, 'message': message})
                    coords = geocode_res["results"][0]["geometry"]["location"]
                    coords = f'{coords["lat"]},{coords["lng"]}'

                # Making sure phone number is 'XXXXXXXXXX', number-only entry is handled on frontend in register.js
                if (phone and len(phone) != 10):
                    message = "Registration unsuccessful. Please make sure phone number is in the correct format."
                    return render(request, "register.html", {'form': form, 'message': message})
                
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
                    u = User.objects.create(first_name=first_name, last_name=last_name, preferred_name=preferred_name, phone=phone, email=email, type=User.Types.DOCTOR, is_active=False)
                    if phone == None:
                        u.sms_notifications = False
                        u.save()
                    # We verified the length/format of ohip_number already and ohip_expiry was verified by the form
                    # If we get an error here, it's because the ohip number was valid, but already exists
                    # However, we already created u, so we must delete it later
                    DoctorInfo.objects.create(user=u, location=address, office_coords=coords)

                except IntegrityError as e:
                    # IntegrityError catches non-unique entries for fields that must be unique, in this case can only be the email
                    
                    # Error message returned to the template
                    return render(request, "docregister.html", {'form': form, 'message': 'Email already registered to existing account!'})
                
                # If nothing goes wrong, set the password.
                # set_password is Django built-in and uses PBKDF2 algorithm and SHA256 hash
                u.set_password(password)
                u.save()

                # Build the token for account confirmation
                domain = get_current_site(request).domain
                uidb64 = urlsafe_base64_encode(force_bytes(u.pk))
                link = reverse('activate', kwargs={'uidb64':uidb64, 'token':default_token_generator.make_token(u),})
                activate_url = getProtocol(request) + '://' + domain + link

                # Send initial SMS consent Message
                # send_mail(
                #     '',
                #     'You will now receive SMS notifications for your booked appointments',
                #     'healthapptdemo@gmail.com',
                #     [u.phone + SMS_CARRIER],
                # )

                # Send a confirmation email
                send_mail(
                    'Confirm your Online Health Account',
                    'Hi,' + u.first_name + '\n\nPlease use the following link to confirm your email:\n' + activate_url + '\n Be aware that this simply confirms that this email is active and in use. Your provided information will have to be verified by our team before you have access to your account.\nYou will be contacted once this process is completed.\n\nThank you\n\nSincerely,\n\nThe MeHealth Team',
                    'healthapptdemo@gmail.com',
                    [u.email],
                )
                return redirect('activateprompt')
            else:
                message = "Registration unsuccessful. Please make sure you have filled all fields in correctly."
                return render(request, "docregister.html", {'form': form, 'message': message})
        
        # If the request is GET, just return an empty form to the template
        else:
            form = SignUpForm()
        return render(request, 'docregister.html', {'form': form})
    return redirect('index')

# View handling AJAX request for checking email and OHIP uniqueness during registration, see register.js line 46
def validate_email_and_ohip(request):
    email = request.GET.get('email1', None)
    data = { 'email_is_taken': User.objects.filter(email__iexact=email).exists(), }
    if request.GET.get('ohip', None) != None:
        ohip = request.GET.get('ohip', None)
        data['ohip_is_taken'] = PatientInfo.objects.filter(ohip_number__iexact=ohip).exists()

    # Prepare an error message based on which field is non-unique
    if data['email_is_taken']:
        data['error_message'] = 'Email already registered to existing account!'
    if 'ohip_is_taken' in data and data['ohip_is_taken']:
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
    context = {
        'message': f'Please check your email for a confirmation message.',
        'valid': True,
    }
    if 'registerdoctor' in request.META.get('HTTP_REFERER'):
        context['message2'] = ' Once confirmed, you will have to await additional verification from our team before being able to log in.'
    return render(request, 'alert.html', context)

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
        if user.type == 'PATIENT':
            user.is_active = True
            user.save()
        elif user.type == 'DOCTOR':
            di = user.userType.more
            di.email_conf = True
            di.save()
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

# View for editing profiles
@login_required
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
                    di.location = form.cleaned_data['location']
                    di.save()
                else:
                    try:
                        # Updates the PatientInfo object associated to u, but have to catch possible non-unique OHIP number
                        pi = PatientInfo.objects.filter(user = u).first()

                        # Getting Address lat/long
                        address = form.cleaned_data['address']
                        postal_code = form.cleaned_data['postal_code']
                        if address != pi.address or postal_code != pi.postal_code:
                            geocode_res = geocode(address, postal_code)
                            if (geocode_res['status'] != 'OK'):
                                message = "Profile Edit unsuccessful. Address and/or Postal Code not found."
                                return render(request, "editprofile.html", {'form': form, 'message': message})
                            coords = geocode_res["results"][0]["geometry"]["location"]
                            coords = f'{coords["lat"]},{coords["lng"]}'
                            pi.address = address
                            pi.postal_code = postal_code
                            pi.address_coords = coords
                        
                        # OHIP checking format 'XXXX-XXX-XXX-XX'
                        ohip_number = form.cleaned_data['ohip'].upper()
                        if (len(ohip_number) != 15 or ohip_number[4] != '-' or ohip_number[8] != '-' or ohip_number[12] != '-'):
                            message = "Profile Edit unsuccessful. Please make sure OHIP number is in the correct format."
                            return render(request, "editprofile.html", {'form': form, 'message': message})
                        ohip_expiry = form.cleaned_data['ohip_expiry']
                        pi.ohip_number = ohip_number
                        pi.ohip_expiry = form.cleaned_data['ohip_expiry']
                        pi.dob = form.cleaned_data['dob']
                        pi.save()
                    except IntegrityError as e:
                        return render(request, "editprofile.html", {'form': form, 'message': 'OHIP number already registered to existing account!'})
                
                # These fields are shared by both Patients and Doctors, so can just save to the general user

                # Making sure phone number is 'XXXXXXXXXX', number-only entry is handled on frontend in register.js
                phone = form.cleaned_data['phone']
                if phone:
                    phone = cleanNumberField(str(phone))
                else:
                    phone = None
                if (phone and len(phone) != 10):
                    message = "Profile Edit unsuccessful. Please make sure phone number is in the correct format."
                    return render(request, "editprofile.html", {'form': form, 'message': message})


                u.first_name = form.cleaned_data['first_name']
                u.preferred_name = form.cleaned_data['preferred_name']
                u.last_name = form.cleaned_data['last_name']
                u.phone = phone
                if phone != None:
                    u.sms_notifications = form.cleaned_data['sms_notis']
                else:
                    u.sms_notifications = False
                u.email_notifications = form.cleaned_data['email_notis']
                u.save()

                newemail = form.cleaned_data['email']

                if newemail != u.email:
                    
                    # Build the token for email change
                    domain = get_current_site(request).domain
                    uidb64 = urlsafe_base64_encode(force_bytes(u.pk))
                    encoded_email = urlsafe_base64_encode(force_bytes(newemail))
                    link = reverse('changeemail', kwargs={'uidb64':uidb64, 'token':default_token_generator.make_token(u), 'newemail':encoded_email,})
                    activate_url = getProtocol(request) + '://' + domain + link


                    ###### MAKE SURE THAT THIS IS UNIQUE TOO
                    if User.objects.filter(email=newemail).exists():
                        message = 'Profile Edit unsuccessful. That email is already taken!.'
                        return render(request, "editprofile.html", {'form': form, 'message': message})

                    u.target_new_email = newemail
                    u.save()
                    send_mail(
                        "Confirm Your MeHealth Account Changes",
                        f'Hi {u.first_name}, \nWe received a request to link this email to your MeHealth account. To confirm this action, please follow the link below. If this was not you, please ignore this email.\n\n{activate_url}\n\nSincerely,\nThe MeHealth Team',
                        "healthapptdemo@gmail.com",
                        [newemail],
                    )

                return redirect('editprofile')

            return redirect('index')
        
        # Handle GET request
        else:
            init = {
                'first_name': u.first_name,
                'preferred_name': u.preferred_name,
                'last_name': u.last_name,
                'email': u.email,
                'init_email': u.email,
                'email_notis': u.email_notifications,
                'sms_notis': u.sms_notifications,
            }
            if u.phone != None:
                init['phone'] = u.formattedPhone
            if u.type == "DOCTOR":
                d = Doctor.objects.filter(id=u.id).first()

                init['qualifications'] = d.more.certification
                if d.more.consultations:
                    init['consultations'] = d.more.consultations
                if d.more.languages:
                    init['languages'] = d.more.languages
                if d.more.location:
                    init['location'] = d.more.location
                #print(init)
                # Put all the existing user information as initial values in the form
                form = DoctorEditForm(initial=init)
                return render(request, 'editprofile.html', {'form': form, 'doctor': d, 'consultations': d.more.consultations.split(', ') if d.more.consultations else None, 'languages': d.more.languages.split(', ') if d.more.languages else None,})
            else:
                p = Patient.objects.filter(id=u.id).first()

                init['address'] = p.more.address
                init['postal_code'] = p.more.postal_code
                init['ohip'] = p.more.ohip_number
                init['ohip_expiry'] = p.more.ohip_expiry
                init['dob']= p.more.dob

                # Put all the existing user information as initial values in the form
                form = PatientEditForm(initial=init)
                return render(request, 'editprofile.html', {'form': form, 'patient': p,})

    # If user is not signed in, template logic will handle appropriate page display
    return render(request, 'editprofile.html')

# View for performing email change after link is sent to user email inbox
def changeemail(request, uidb64, token, newemail):
    try:
        # Query User using decoded UID
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    newemail = force_text(urlsafe_base64_decode(newemail))

    # This will fail if the user has already used the link to changed their email, the token is invalid, the UID is invalid, or the user has requested to change to another email
    if user is not None and default_token_generator.check_token(user, token) and user.target_new_email == newemail:
        user.email = newemail
        user.target_new_email = None
        user.save()
        return redirect('emailchangesuccess')
    else:
        return redirect('emailchangefail')

@login_required
def emailchangecancel(request):
    u = request.user
    u.target_new_email = None
    u.save()
    return redirect('editprofile')

def emailchangesuccess(request):
    message = "You have successfully changed your email."
    return render(request, 'alert.html', { 'message': message, 'valid': True })

def emailchangefail(request):
    message = "Your email change request is either invalid or has expired."
    return render(request, 'alert.html', { 'message': message, 'valid': False })

@login_required
def findpharmacy(request):
    u = request.user
    if u.is_authenticated and u.type == 'PATIENT':
        if request.method == 'GET':
            pinfo = u.userType.more
            nearby = get_nearby(pinfo.address_coords, 'pharmacy')
            #print(nearby['status'])
            if nearby['status'] != 'OK':
                print(nearby['error_message'])
                pprint(nearby['results'])
            if nearby['status'] != 'OK':
               return render(request, 'findpharmacy.html', { 'querytext':f'search?key={GOOGLE_MAPS_API_KEY}&q=pharmacies+{pinfo.postal_code[:3]}&zoom=13&center={pinfo.address_coords}', 'message':'Location Service Error. Please check your address and postal code.' })
            nearby = nearby['results']
            data = []
            for place in nearby:
                ignore = ['BPG', 'ANIMAL', 'VET', 'HM GROUPS', 'FOOD', 'NUTRITION']
                ignored = False
                for term in ignore:
                    if term in place['name'].upper():
                        ignored = True
                if not ignored:
                    data.append({'name': place['name'], 'address': place['vicinity'], 'place_id':place['place_id']})
            #print(pinfo.postal_code)
            #print(pinfo.address_coords)  
            #return render(request, 'findpharmacy.html', { 'querytext':f'place?key={GOOGLE_MAPS_API_KEY}&q=place_id:ChIJJezxiLRCK4gRaYFq3-uLzcI' })
            return render(request, 'findpharmacy.html', { 'querytext':f'search?key={GOOGLE_MAPS_API_KEY}&q=pharmacies+{pinfo.postal_code[:3]}&zoom=13&center={pinfo.address_coords}', 'places':data })
            #return render(request, 'findpharmacy.html', { 'querytext':f'view?key={GOOGLE_MAPS_API_KEY}&center=43.56465615772579,-79.67794135999671&zoom=9' })
        else:
            pid = request.POST.get('pharmacy-id', None)
            if pid:
                patient_info = PatientInfo.objects.get(user=u)
                if patient_info:
                    r = find_place_by_place_id(pid)
                    if r['status'] == 'OK':
                        place = r['result']
                        pharmacy = place['name'] + ', ' + place['formatted_address']
                        patient_info.pharmacy = pharmacy
                        patient_info.save()
                return redirect('editprofile')
            else:
                return redirect('findpharmacy')
            return redirect('index')
    return redirect('index')

def focuspharmacy(request):
    pid = request.GET.get('pharmacy-id', None)
    return JsonResponse({})
    ## find the actual formatted address here