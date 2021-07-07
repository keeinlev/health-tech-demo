from django.shortcuts import render, redirect
from django.urls import reverse
from graph.auth_helper import remove_token

# Create your views here.

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def login_redir(request):
    if (request.user.is_authenticated):
        remove_token(request)
        if (request.user.type == "DOCTOR"):
            return redirect('doctordashboard')
        else:
            return redirect('index')

def handler404(request, exception):
    response = render(request, 'alert.html', {'message': 'Oops! An error occured (Error code 404)', 'valid': False})
    response.status_code = 404
    return response

def handler500(request):
    response = render(request, 'alert.html', {'message': 'Oops! An error occured (Error code 500)', 'valid': False})
    response.status_code = 500
    return response