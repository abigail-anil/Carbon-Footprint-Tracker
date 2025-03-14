from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .forms import UserSignUpForm

def sign_up(request):
    if request.method == "POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after signup
            messages.success(request, f'Account created for {user.username}.')
            return redirect('/')
    else:
        form = UserSignUpForm()
        
    return render(request, 'users/signup.html', {'form': form})

def verify_email(request):
    messages.success(request, "Your email has been verified.")
    return render(request, 'users/verify_email.html')


def sign_out(request):
    logout(request)
    return render(request, 'users/signout.html')
