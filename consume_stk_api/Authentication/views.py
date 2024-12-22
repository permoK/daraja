from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from .forms import SignUpForm

from django.views import View
from django.contrib.auth import login,logout, authenticate
# Create your views here.

def index(request):
    return HttpResponse("hello Authentication")

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('Authentication:login_user')
    template_name = 'tutor_signup.html'

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.capitalize()}: {error}")
        return super().form_invalid(form)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Tutor account created successfully!")
        return response

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('Username')
        password = request.POST.get('Password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Determine the redirect URL
            if user:
                redirect_url = reverse('Authentication:index')
            else:
                redirect_url = '/'
            
            # Return a response with HX-Redirect header
            response = HttpResponse()
            response['HX-Redirect'] = redirect_url
            return response
        else:
            return render(request, 'loginresult.html')
    
    return render(request, 'login.html')

def redirect_user(user):
    if user.user_type == 'tutor':
        return redirect('Tutor:tutor_dashboard')
    elif user.user_type == 'parent':
        return redirect('Client:parent_dashboard')
    else:
        return redirect('/')


def logout_user(request):
    logout(request)
    messages.success(request, 'You have successfully logged out')

    return redirect('Authentication:login_user')
