from django.shortcuts import render, redirect

# Create your views here.

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def login_redir(request):
    if (request.user.is_authenticated):
        if (request.user.type == "DOCTOR"):
            return redirect('doctordashboard')
        else:
            return redirect('index')