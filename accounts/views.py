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


# Create your views here.

def register(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            preferred_name = form.cleaned_data['preferred_name']
            dob = form.cleaned_data['dob']
            email = form.cleaned_data['email1']
            password = form.cleaned_data['password1']
            phone = str(form.cleaned_data['phone'])
            #phone = str(form.cleaned_data['phone1']) + str(form.cleaned_data['phone2']) + str(form.cleaned_data['phone3'])
            ohip_number = str(form.cleaned_data['ohip'])
            ohip_number = ohip_number[:4] + '-' + ohip_number[4:7] + '-' + ohip_number[7:]
            #ohip_number = str(form.cleaned_data['ohip1']) + '-' + str(form.cleaned_data['ohip2']) + '-' + str(form.cleaned_data['ohip3'])
            ohip_version_code = form.cleaned_data['ohip_version']
            ohip_number = ohip_number + '-' + ohip_version_code
            ohip_number = ohip_number.upper()
            ohip_expiry = form.cleaned_data['ohip_expiry']
            if len(phone) != 10 or len(ohip_number) != 15:
                message = "Registration unsuccessful. Please make sure phone and OHIP numbers are in the correct format."
                return render(request, "register.html", {'form': form, 'message': message})
            if (email != form.cleaned_data['email2'] or password != form.cleaned_data['password2']):
                message = "Registration unsuccessful. Please make sure emails and passwords match."

                return render(request, "register.html", {'form': form, 'message': message})
            try:
                u = User.objects.create(first_name=first_name, last_name=last_name, preferred_name=preferred_name, phone=phone, email=email, password=password, dob=dob, type=User.Types.PATIENT)
                PatientInfo.objects.create(user=u, ohip_number=ohip_number, ohip_expiry=ohip_expiry)
            except IntegrityError as e:
                #print(e.__cause__)
                cause = str(e.__cause__)
                cleancause = cause[cause.index("UNIQUE constraint failed: ") + len("UNIQUE constraint failed: "):]
                unique_constraint = cleancause[cleancause.index('.') + 1:].capitalize().replace('_', ' ')
                #print(unique_constraint)
                if unique_constraint == 'Ohip number':
                    unique_constraint = 'OHIP Number'
                    User.objects.last().delete()
                #print(User.objects.all())
                return render(request, "register.html", {'form': form, 'message': unique_constraint + ' already registered to existing account!'})
            
            u.set_password(password)
            u.is_active = False
            u.save()
            domain = get_current_site(request).domain
            uidb64 = urlsafe_base64_encode(force_bytes(u.pk))
            link = reverse('activate', kwargs={'uidb64':uidb64, 'token':default_token_generator.make_token(u),})
            activate_url = 'http://' + domain + link
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
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})

def editprofile(request):
    u = request.user
    if u.is_authenticated:
        form = None
        if request.method == 'POST':
            if u.type == "DOCTOR":
                form = DoctorEditForm(request.POST)
            else:
                form = PatientEditForm(request.POST)
            if form.is_valid():
                if u.type == 'DOCTOR':
                    di = DoctorInfo.objects.filter(user = u).first()
                    di.certification = form.cleaned_data['qualifications']
                    di.consultations = form.cleaned_data['consultations']
                    di.languages = form.cleaned_data['languages']
                    #di.meeting_url = form.cleaned_data['meeting_url']
                    di.save()
                else:
                    try:
                        pi = PatientInfo.objects.filter(user = u).first()
                        pi.ohip_number = str(form.cleaned_data['ohip1']) + '-' + str(form.cleaned_data['ohip2']) + '-' + str(form.cleaned_data['ohip3']) + '-' + form.cleaned_data['ohip_version'].upper()
                        pi.ohip_expiry = form.cleaned_data['ohip_expiry']
                        pi.save()
                    except IntegrityError as e:
                        return render(request, "editprofile.html", {'form': form, 'message': 'OHIP number already registered to existing account!'})
                
                u.first_name = form.cleaned_data['first_name']
                u.last_name = form.cleaned_data['last_name']
                u.dob = form.cleaned_data['dob']
                u.phone = str(form.cleaned_data['phone1']) + str(form.cleaned_data['phone2']) + str(form.cleaned_data['phone3'])
                u.save()

            return redirect('index')
        else:
            if u.type == "DOCTOR":
                d = Doctor.objects.filter(id=u.id).first()
                form = DoctorEditForm(initial={
                    'first_name': d.first_name,
                    'last_name': d.last_name,
                    'dob': d.dob,
                    'phone1': d.phone[:3],
                    'phone2': d.phone[3:6],
                    'phone3': d.phone[6:],
                    'qualifications': d.more.certification,
                    'consultations': d.more.consultations,
                    'languages': d.more.languages,
                    #'meeting_url': d.more.meeting_url,
                })
                return render(request, 'editprofile.html', {'form': form, 'doctor': d, 'consultations': d.more.consultations.split(', '), 'languages': d.more.languages.split(', '),})
            else:
                p = Patient.objects.filter(id=u.id).first()
                form = PatientEditForm(initial={
                    'first_name': p.first_name,
                    'last_name': p.last_name,
                    'dob': p.dob,
                    'phone1': p.phone[:3],
                    'phone2': p.phone[3:6],
                    'phone3': p.phone[6:],
                    'ohip1': p.more.ohip_number[:4],
                    'ohip2': p.more.ohip_number[5:8],
                    'ohip3': p.more.ohip_number[9:12],
                    'ohip_version': p.more.ohip_number[13:],
                    'ohip_expiry': p.more.ohip_expiry,
                })
                return render(request, 'editprofile.html', {'form': form, 'patient': p,})
    return render(request, 'editprofile.html')


def validate_email(request):
    email = request.GET.get('email1', None)
    ohip = str(request.GET.get('ohip', None))
    ohip_version = request.GET.get('ohip_version', None)
    ohip = '-'.join([ohip[:4], ohip[4:7], ohip[7:], str(ohip_version)])
    data = {
        'email_is_taken': User.objects.filter(email__iexact=email).exists(),
        'ohip_is_taken': PatientInfo.objects.filter(ohip_number__iexact=ohip).exists(),
    }
    if data['email_is_taken']:
        data['error_message'] = 'Email already registered to existing account!'
    if data['ohip_is_taken']:
        if 'error_message' in data:
            data['error_message'] += '<br />OHIP Number already registered to existing account!'
        else:
            data['error_message'] = "OHIP Number already registered to existing account!"
    return JsonResponse(data)

def login(request):
    return render(request, 'login.html')

def logout_redir(request):
    user = request.user
    print(user)
    if (user.is_authenticated):
        if (user.type == 'DOCTOR'):
            remove_user_and_token(request)
        return redirect('logout')
        print('logout')
    return redirect('index')

def doctorlogin(request):
    pass

def activateprompt(request):
    message = f'Please check your email for a confirmation message.'
    return render(request, 'alert.html', { 'message': message, 'valid': True })

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('confirmsuccess')
    else:
        return redirect('confirmfail')

def confirmsuccess(request):
    message = f'Thank you for confirming your email.'
    return render(request, 'alert.html', { 'message': message, 'valid': True })

def confirmfail(request):
    return render(request, 'alert.html', { 'message': 'Email activation invalid.', 'valid': False })