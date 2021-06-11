from django.shortcuts import render, redirect
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