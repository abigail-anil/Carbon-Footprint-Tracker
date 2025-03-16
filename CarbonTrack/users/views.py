from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .forms import UserSignUpForm
from .utils import subscribe_email_to_sns_topic
from django.conf import settings  # Import settings
import logging

logger = logging.getLogger(__name__)  # Get a logger instance

def sign_up(request):
    success = False
    if request.method == "POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after signup
            messages.success(request, f'Account created for {user.username}. You will receive a confirmation email to subscribe to notifications.')

            # SNS Subscription Logic
            topic_arn = settings.SNS_TOPIC_ARN  # Get from settings
            email = user.email

            if topic_arn and email:
                try:
                    subscribe_email_to_sns_topic(topic_arn, email)
                    success = True  # Set success to True ONLY after successful SNS subscription
                except Exception as e:
                    messages.error(request, f"Error subscribing to notifications: {e}")
                    logger.error(f"SNS subscription error: {e}")

            return redirect('/')
        else:
            messages.error(request, "Please correct the errors below.")
            
    else:
        form = UserSignUpForm()

    return render(request, 'users/signup.html', {'form': form, 'success': success})

def verify_email(request):
    messages.success(request, "Your email has been verified.")
    return render(request, 'users/verify_email.html')


def sign_out(request):
    logout(request)
    return render(request, 'users/signout.html')
