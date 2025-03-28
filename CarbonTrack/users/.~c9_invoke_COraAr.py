from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .forms import UserSignUpForm
import base64  # Import base64 module for encoding

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
    
    # Open the image file, encode it to Base64, and decode to a string
    # Replace "path/to/your/image.png" with the actual file path on your system.
    with open("path/to/your/image.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Pass both the form and the Base64-encoded image string to the template context
    return render(request, 'users/signup.html', {
        'form': form,
        'base64_image_string': encoded_string,
    })

def sign_out(request):
    logout(request)
    return render(request, 'users/signout.html')
